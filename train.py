import torch
import torch.nn as nn
import torch.optim as optim
from MyDataset import train_loader, test_loader
import time
from tqdm import tqdm
import config
from torch.utils.tensorboard import SummaryWriter
from models import Resnet18WithSoftmax as resnet
import os

def train(model : nn.Module, optimizer : optim.Optimizer, criterion, train_loader, i):
    model.train() 
    running_loss = 0.0
    correct = 0.0
    pars = tqdm(train_loader, leave=False)
    for inputs, labels in pars:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        pars.set_description(f"Training loss {loss:.4f}")
        loss.backward()
        optimizer.step()
        _, preds = torch.max(outputs, 1)
        correct += torch.sum(preds == labels.data)
        running_loss += loss.item() * inputs.size(0)
    epoch_loss = running_loss / len(train_loader.dataset) 
    epoch_acc = correct.double() / len(train_loader.dataset)
    writer.add_scalar('train_loss', epoch_loss, i)
    writer.add_scalar('train_acc', epoch_acc, i)
    return epoch_loss, epoch_acc

def test(model : nn.Module, criterion, test_loader, i):
    model.eval()
    running_loss = 0.0
    correct = 0
    with torch.no_grad(): 
        pars = tqdm(test_loader, leave=False)
        for inputs, labels in pars:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            pars.set_description(f"Testing loss {loss:.4f}")
            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct += torch.sum(preds == labels.data)
    epoch_loss = running_loss / len(test_loader.dataset)
    epoch_acc = correct.double() / len(test_loader.dataset)
    writer.add_scalar('test_loss', epoch_loss, i)
    writer.add_scalar('test_acc', epoch_acc, i)
    return epoch_loss, epoch_acc

writer = SummaryWriter('logs/ResNet18')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = resnet.Resnet18WithSoftmax().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE, weight_decay=config.WEITHT_DECAY)

from PIL import ImageFile 
ImageFile.LOAD_TRUNCATED_IMAGES = True

fine_tuning = False
if fine_tuning:
    model.load_state_dict(torch.load(r"checkpoint/ResNet18_Epoch_94.pth")) 
print(f'Fine Tuning : {fine_tuning}')

t = time.time()
if os.path.exists(config.LOGTXT_NAME):
    os.remove(config.LOGTXT_NAME)
for epoch in range(config.EPOCH):
    train_loss, train_acc = train(model, optimizer, criterion, train_loader, epoch)
    test_loss, test_acc = test(model, criterion, test_loader, epoch)
    log = f"Epoch {epoch+1}/{config.EPOCH} - Train Loss: {train_loss:.4f} - Train Acc: {train_acc:.4f} - Test Loss: {test_loss:.4f} - Test Acc: {test_acc:.4f} - Time: {time.time() - t:.2f}s"
    with open(config.LOGTXT_NAME, 'a+') as f:
        f.write(log + "\n")
    print(log)
    torch.save(model.state_dict(), f"checkpoint/ResNet18_Epoch_{epoch+1}.pth")
writer.close()