# import collections

import torch
import torch.nn as nn
import torch.nn.functional as F

VERBOSE = False

class PatchEmbeddings(nn.Module):
    def __init__(
        self, 
        image_size,
        patch_size,
        hidden_size,
        num_channels = 3,      # 3 for RGB, 1 for Grayscale
        ):
        super().__init__()

        # set the number of patches
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_patches = image_size // patch_size
        # set the size of the patch embeddings
        self.hidden_size = hidden_size

        # patches
        self.projection = nn.Conv2d(self.num_channels, self.hidden_size, kernel_size=self.patch_size, stride=self.patch_size, bias=False)


        

    def forward(self, x):
        batch_size, num_channels, height, width = x.shape
        if num_channels != self.num_channels:
            raise ValueError(
                "Make sure that the channel dimension of the pixel values match with the one set in the configuration."
            )

        # Calculate Patch Embeddings, then flatten into
        # batched 1D sequence (batch_size, seq_length, hidden_size)
        embeddings = self.projection(x)
        embeddings = torch.flatten(embeddings, 2).view(-1, self.num_patches**2, self.hidden_size)

        if VERBOSE: print(f"PatchEmbeddings out: {embeddings.shape}, expected ({batch_size}, {self.num_patches**2}, {self.hidden_size})")
        return embeddings

class PositionEmbedding(nn.Module):
    def __init__(
        self,
        num_patches,
        hidden_size,
        ):
        super().__init__()
        
        # Specify [CLS] and positional embedding as learnable parameters

        self.num_patches = num_patches
        self.cls_token = nn.Parameter(torch.randn(1 ,1 , hidden_size))
        self.position_embeddings = nn.Parameter(torch.randn(1, 1+num_patches**2, hidden_size))


    def forward(self,embeddings):

        # Concatenate [CLS] token with embedded patch tokens
        cls_token = self.cls_token.repeat(embeddings.shape[0], 1, 1)
        embeddings = torch.cat([cls_token, embeddings], dim=1)

        # Then add positional encoding to each token
        embeddings += self.position_embeddings
        if VERBOSE: print(f"PositionEmbedding out: {embeddings.shape}")
        return embeddings

class GELU(nn.Module):
    # Gelu activation function
    def forward(self, x: torch.Tensor):
        return x * torch.sigmoid(1.702 * x)

class ResidualAttentionBlock(nn.Module):
    def __init__(self, d_model: int, n_head: int):
        super().__init__()
        self.d_model = d_model
        self.n_head = n_head

        self.norm_layer1 = nn.LayerNorm(d_model)
        self.attn = nn.MultiheadAttention(d_model, n_head)  
        self.res_2 = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Sequential(
                nn.LazyLinear(n_head),
                nn.GELU(),
                nn.LazyLinear(d_model),
                nn.GELU(),
            )
        )
    def forward(self, x: torch.Tensor):


        # LayerNorm -> Multi-head Attention
        # Residual connection against x
        out1 = self.norm_layer1(x)
        out1, _ = self.attn(out1, out1, out1)
        out1 += x

        # LayerNorm -> MLP Block
        # Residual connection against x

        out2 = self.res_2(out1)
        out = out2 + x
        if VERBOSE: print(f"ResidualAttentionBlock out: {out.shape}")

        return out

class Transformer(nn.Module):
    def __init__(self, width: int, layers: int, heads: int):
        super().__init__()
        self.width = width
        self.layers = layers
        self.resblocks = nn.Sequential(*[ResidualAttentionBlock(width, heads) for _ in range(layers)])

    def forward(self, x: torch.Tensor):
        x = x.permute(1, 0, 2)  # (batch_size, seqlen, dim) -> (seqlen, batch_size, dim)
        x = self.resblocks(x)
        x = x.permute(1, 0, 2)  # (seqlen, batch_size, dim) -> (batch_size, seqlen, dim)
        
        if VERBOSE: print(f"Transformer out: {x.shape}")
        return x

class ViT(nn.Module):
    def __init__(
        self, 
        image_size: int, 
        patch_size: int, 
        num_channels: int,
        hidden_size: int, 
        layers: int, 
        heads: int):
        super().__init__()
        self.hidden_size = hidden_size
        num_patches = image_size // patch_size
        self.patch_embed = PatchEmbeddings(image_size, patch_size, hidden_size, num_channels)

        self.pos_embed = PositionEmbedding(num_patches, hidden_size)

        self.ln_pre = nn.Linear(hidden_size, hidden_size)
        
        self.transformer = Transformer(hidden_size, layers, heads)

        self.ln_post = nn.LazyLinear(hidden_size)


    def forward(self, x: torch.Tensor):
        embeddings = self.pos_embed(self.patch_embed(x))

        out = self.ln_pre(embeddings)
        out = self.transformer(out)
        out = out[:, 0]
        # print(out.shape)
        out = self.ln_post(out)


        if VERBOSE: print(f"ViT out: {out.shape}")

        return out

class ClassificationHead(nn.Module):
    def __init__(
        self, 
        hidden_size: int,
        num_classes: int = 10,
        ):
        super().__init__()
        self.classifier = nn.Linear(hidden_size, num_classes)

    def forward(
        self, 
        feats: torch.Tensor,
        ) -> torch.Tensor:
        out = self.classifier(feats)
        if VERBOSE: print(f"ClassificationHead out: {out.shape}")
        return out

class LinearEmbeddingHead(nn.Module):
    def __init__(
        self, 
        hidden_size: int,
        embed_size: int = 64,
        ):
        super().__init__()
        self.embed_size = embed_size
        self.projection = nn.Linear(hidden_size, embed_size)

    def forward(
        self, 
        feats: torch.Tensor,
        ) -> torch.Tensor:
        out = self.projection(feats)
        if VERBOSE: print(f"LinearEmbeddingHead out: {out.shape}")
        return out

class Conv(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
        nn.Conv2d(input_dim, output_dim, 2),
        nn.BatchNorm2d(output_dim),
        nn.MaxPool2d(2),
        nn.GELU()
        )
    
    def forward(self, x):
        return self.net(x)
    
class Lin(nn.Module):
    def __init__(self, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.LazyLinear(output_dim),
            nn.BatchNorm1d(output_dim),
            nn.GELU()
        )
    
    def forward(self, x):
        return self.net(x)

class CNN(nn.Module):
    def __init__(self, input_dim = 1, num_classes = 47):
        super().__init__()
        self.conv_network_dims = [input_dim, 512, 256, 128]
        self.conv_net = nn.ModuleList([Conv(self.conv_network_dims[i], self.conv_network_dims[i+1]) for i in range(len(self.conv_network_dims) - 1)])

        fc_net_dims = [128, 64]
        self.fc_net = nn.ModuleList([Lin(fc_net_dims[i]) for i in range(len(fc_net_dims))])

        self.output_layer = nn.Sequential(
            nn.LazyLinear(num_classes),
            nn.BatchNorm1d(num_classes),
            nn.Sigmoid()
        )

    def forward(self, x):
        batch = x.shape[0]
        for layer in self.conv_net:
            x = layer(x)
            # print(x.shape)
        x = x.reshape(batch, -1)
        # print(x.shape)
        for layer in self.fc_net:
            x = layer(x)
        return self.output_layer(x)
