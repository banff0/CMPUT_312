import torch 
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torchvision.transforms import Compose, ToTensor, Normalize, RandomRotation, RandomHorizontalFlip
from torch.optim import lr_scheduler
from tqdm import tqdm

from models import CNN

# hyper params for model
BATCH_SIZE = 16
NUM_CLASSES = 47
LEARNING_RATE = 0.001
DECAY_RATE = 0.0005
NUM_EPOCHS = 50

# data augmentation
transforms = Compose([
    RandomRotation([-15, 15]),
    RandomHorizontalFlip(1),
    ToTensor(),
    Normalize((0.5, ), (0.5, )),
    ])

def train_model():
    # how to load the dataset
    # split = "bymerge"
    split = "balanced"
    # load the train and test datasets
    train_dataset = torchvision.datasets.EMNIST(root='./data', split=split, train=True, download=True, transform=transforms)
    test_dataset = torchvision.datasets.EMNIST(root='./data', split=split, train=False, download=True, transform=transforms)

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # load the model
    model = CNN(1, NUM_CLASSES)

    # run on gpu is available
    if torch.cuda.is_available():
        print("RUNNING ON GPU")
        model = model.cuda()

    # CE loss
    criterion = nn.CrossEntropyLoss()

    # AdamW solves issues with Adam
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=DECAY_RATE)

    # define our LR scheduler
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    # Track the models accuracy
    best_acc = 0.0

    # train for N epochs
    for epoch in range(NUM_EPOCHS):
        # iter over the batches
        for i, (x, labels) in enumerate(tqdm(train_loader)):
            model.train()
            # load data onto GPU if avialable
            if torch.cuda.is_available():
                x = x.cuda()
                labels = labels.cuda()
            # get the model preds, and calculate the loss
            outs = model(x)
            loss = criterion(outs, labels)
            
            # take the SGD step
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if (i+1) % len(train_loader) == 0:
                print ('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'.format(epoch+1, NUM_EPOCHS, i+1, len(train_loader), loss.item()))
        # update the LR at the end of each epoch
        exp_lr_scheduler.step()

        # check the model on the test set with no learning
        test_acc = test_model(model, test_loader=test_loader)
        # save the model if we have new best acc
        if test_acc > best_acc:
            best_acc = test_acc
            state_dict = {
                "model": model.state_dict(),
                "acc": best_acc,
            }
            torch.save(state_dict, f"saved_models/TEST{split}_CNN_no_rot.pt")
            print("Best test acc:", best_acc)
        print()

def test_model(model, test_loader):
    model.eval()
    # make sure to not update the gradients
    with torch.no_grad():
        correct = 0
        total = 0
        # iter over the test set in batches
        for images, labels in test_loader:
            # load the data to the gpu if avial
            if torch.cuda.is_available():
                images = images.cuda()
                labels = labels.cuda()
            outs = model(images)
            _, predicted = torch.max(outs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        print('Test Accuracy: {} %'.format(100 * correct / total))
    # return the test accuracy of the current model
    return correct / total

train_model()