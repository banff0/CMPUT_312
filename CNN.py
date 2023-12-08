import torch 
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torchvision.transforms import Compose, ToTensor, Normalize, RandomRotation, RandomHorizontalFlip
from torch.optim import lr_scheduler
from tqdm import tqdm


BATCH_SIZE = 16
NUM_CLASSES = 47
LEARNING_RATE = 0.001
DECAY_RATE = 0.0005
NUM_EPOCHS = 50


transforms = Compose([
    RandomRotation([-15, 15]),
    RandomHorizontalFlip(1),
    ToTensor(),
    Normalize((0.5, ), (0.5, )),
    ])


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

def train_model():
    # split = "bymerge"
    split = "balanced"
    train_dataset = torchvision.datasets.EMNIST(root='./data', split=split, train=True, download=True, transform=transforms)
    test_dataset = torchvision.datasets.EMNIST(root='./data', split=split, train=False, download=True, transform=transforms)

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    model = CNN(1, NUM_CLASSES)

    # Classifier
    if torch.cuda.is_available():
        print("RUNNING ON GPU")
        model = model.cuda()

    # Use cross entropy
    criterion = nn.CrossEntropyLoss()

    # Specify optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=DECAY_RATE)

    exp_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    # Evaluate at the end of each epoch
    best_acc = 0.0

    for epoch in range(NUM_EPOCHS):
        for i, (x, labels) in enumerate(tqdm(train_loader)):
            model.train()

            if torch.cuda.is_available():
                x = x.cuda()
                labels = labels.cuda()

            outs = model(x)
            loss = criterion(outs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if (i+1) % len(train_loader) == 0:
                print ('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'.format(epoch+1, NUM_EPOCHS, i+1, len(train_loader), loss.item()))
        exp_lr_scheduler.step()

        test_acc = test_model(model, test_loader=test_loader)
        if test_acc > best_acc:
            best_acc = test_acc
            state_dict = {
                "model": model.state_dict(),
                "acc": best_acc,
            }
            torch.save(state_dict, f"EMNIST{split}_CNN_no_rot.pt")
            print("Best test acc:", best_acc)
        print()

def test_model(model, test_loader):
    model.eval()
    with torch.no_grad():
        correct = 0
        total = 0
        for images, labels in test_loader:
            if torch.cuda.is_available():
                images = images.cuda()
                labels = labels.cuda()
            outs = model(images)
            _, predicted = torch.max(outs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        print('Test Accuracy: {} %'.format(100 * correct / total))
    return correct / total

train_model()