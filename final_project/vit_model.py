# import collections

import torch
import torch.nn as nn
import torch.nn.functional as F

VERBOSE = False

class PatchEmbeddings(nn.Module):
    """TODO: (0.5 out of 8) Calculates patch embedding
    of shape `(batch_size, seq_length, hidden_size)`.
    """
    def __init__(
        self, 
        image_size: int,
        patch_size: int,
        hidden_size: int,
        num_channels: int = 3,      # 3 for RGB, 1 for Grayscale
        ):
        super().__init__()
        # #########################
        # Finish Your Code HERE
        # #########################

        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_patches = image_size // patch_size
        self.hidden_size = hidden_size

        # self.projection = (image_size**2) / (p**2)
        self.projection = nn.Conv2d(self.num_channels, self.hidden_size, kernel_size=self.patch_size, stride=self.patch_size, bias=False)
        
        # #########################

        

    def forward(
        self, 
        x: torch.Tensor,
        ) -> torch.Tensor:
        batch_size, num_channels, height, width = x.shape
        if num_channels != self.num_channels:
            raise ValueError(
                "Make sure that the channel dimension of the pixel values match with the one set in the configuration."
            )
        
        # #########################
        # Finish Your Code HERE
        # #########################

        # Calculate Patch Embeddings, then flatten into
        # batched 1D sequence (batch_size, seq_length, hidden_size)
        embeddings = self.projection(x)
        embeddings = torch.flatten(embeddings, 2).view(-1, self.num_patches**2, self.hidden_size)

        if VERBOSE: print(f"PatchEmbeddings out: {embeddings.shape}, expected ({batch_size}, {self.num_patches**2}, {self.hidden_size})")
        # #########################
        return embeddings

class PositionEmbedding(nn.Module):
    def __init__(
        self,
        num_patches,
        hidden_size,
        ):
        """TODO: (0.5 out of 8) Given patch embeddings, 
        calculate position embeddings with [CLS] and [POS].
        """
        super().__init__()
        # #########################
        # Finish Your Code HERE
        # #########################
        
        # Specify [CLS] and positional embedding as learnable parameters

        self.num_patches = num_patches
        self.cls_token = nn.Parameter(torch.randn(1 ,1 , hidden_size))
        self.position_embeddings = nn.Parameter(torch.randn(1, 1+num_patches**2, hidden_size))

        # #########################

    def forward(
        self,
        embeddings: torch.Tensor
        ) -> torch.Tensor:
        # #########################
        # Finish Your Code HERE
        # #########################

        # Concatenate [CLS] token with embedded patch tokens
        

        cls_token = self.cls_token.repeat(embeddings.shape[0], 1, 1)
        embeddings = torch.cat([cls_token, embeddings], dim=1)

        # Then add positional encoding to each token

        #################################################################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        embeddings += self.position_embeddings
        if VERBOSE: print(f"PositionEmbedding out: {embeddings.shape}")
        # #########################
        return embeddings

class GELU(nn.Module):
    def forward(self, x: torch.Tensor):
        return x * torch.sigmoid(1.702 * x)

class ResidualAttentionBlock(nn.Module):
    """TODO: (0.25 out of 8) Residual Attention Block.
    """
    def __init__(self, d_model: int, n_head: int):
        super().__init__()
        # #########################
        # Finish Your Code HERE
        # #########################
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
        # #########################

    def forward(self, x: torch.Tensor):

        # #########################
        # Finish Your Code HERE
        # #########################

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

        # #########################

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
    """TODO: (0.5 out of 8) Vision Transformer.
    """
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
        # #########################
        # Finish Your Code HERE
        # #########################
        num_patches = image_size // patch_size
        self.patch_embed = PatchEmbeddings(image_size, patch_size, hidden_size, num_channels)

        self.pos_embed = PositionEmbedding(num_patches, hidden_size)

        self.ln_pre = nn.Linear(hidden_size, hidden_size)
        
        self.transformer = Transformer(hidden_size, layers, heads)

        self.ln_post = nn.LazyLinear(hidden_size)

        # #########################


    def forward(self, x: torch.Tensor):
        # #########################
        # Finish Your Code HERE
        # #########################
        embeddings = self.pos_embed(self.patch_embed(x))

        out = self.ln_pre(embeddings)
        out = self.transformer(out)
        out = out[:, 0]
        # print(out.shape)
        out = self.ln_post(out)


        if VERBOSE: print(f"ViT out: {out.shape}")
        # #########################

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
    """TODO: (0.25 out of 8) Given features from ViT, generate linear embedding vectors.
    """
    def __init__(
        self, 
        hidden_size: int,
        embed_size: int = 64,
        ):
        super().__init__()
        self.embed_size = embed_size
        # #########################
        # Finish Your Code HERE
        # #########################
        self.projection = nn.Linear(hidden_size, embed_size)
        # #########################

    def forward(
        self, 
        feats: torch.Tensor,
        ) -> torch.Tensor:
        # #########################
        # Finish Your Code HERE
        # #########################
        out = self.projection(feats)
        if VERBOSE: print(f"LinearEmbeddingHead out: {out.shape}")
        # #########################
        return out
