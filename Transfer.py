import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import torch.backends.cudnn as cudnn
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
from tqdm import tqdm

DEVICE = "cpu"
if torch.cuda.is_available():
    DEVICE = "cuda"
NUM_EPOCHS = 25
BATCH_SIZE = 16



def train_model():
    train_dataset = torchvision.datasets.EMNIST(root='./data', split="bymerge", train=True, download=True, transform=transforms)
    test_dataset = torchvision.datasets.EMNIST(root='./data', split="bymerge", train=False, download=True, transform=transforms)

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    model = models.swin_b(weights='IMAGENET1K_V1')
    num_ftrs = model.fc.in_features
    # Here the size of each output sample is set to 2.
    # Alternatively, it can be generalized to ``nn.Linear(num_ftrs, len(class_names))``.
    model.fc = nn.Linear(num_ftrs, 47)

    model = model.to(DEVICE)

    criterion = nn.CrossEntropyLoss()

    # Observe that all parameters are being optimized
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    # Decay LR by a factor of 0.1 every 7 epochs
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
            torch.save(state_dict, "EMNIST_SWIN.pt")
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
