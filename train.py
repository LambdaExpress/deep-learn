import os
import time
import warnings
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from PIL import ImageFile
from contextlib import contextmanager
from my_dataset import MyDataset
from models import resnet18_with_softmax as resnet
import config
from tqdm import tqdm

warnings.filterwarnings("ignore")
ImageFile.LOAD_TRUNCATED_IMAGES = True

@contextmanager
def open_log_file(file_name):
    """
    A context manager that opens and closes the log file.
    """
    with open(file_name, 'a+') as f:
        yield f
    f.close()

def train_and_test(model, optimizer, criterion, train_loader, test_loader, epoch):
    """
    Trains and tests the model for one epoch.

    Args:
        model: The ResNet18 model.
        optimizer: The optimizer used for training the model.
        criterion: The loss function used for training and testing the model.
        train_loader: The data loader used for training the model.
        test_loader: The data loader used for testing the model.
        epoch: The current epoch number.

    Returns:
        The training loss, training accuracy, testing loss, and testing accuracy for the epoch.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.train()
    train_loss = 0
    train_correct = 0
    train_total = 0
    pars = tqdm(train_loader, leave=False)
    for inputs, labels in pars:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        pars.set_description(f"Epoch:{epoch + 1} Training Loss {loss.item():.3f}")
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        _, predicted = outputs.max(1)
        train_total += labels.size(0)
        train_correct += predicted.eq(labels).sum().item()

    train_loss /= len(train_loader)
    train_acc = train_correct / train_total

    model.eval()
    test_loss = 0
    test_correct = 0
    test_total = 0
    with torch.no_grad():
        pars = tqdm(test_loader, leave=False)
        for inputs, labels in pars:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            pars.set_description(f"Epoch:{epoch + 1} Testing Loss {loss.item():.3f}")
            test_loss += loss.item()
            _, predicted = outputs.max(1)
            test_total += labels.size(0)
            test_correct += predicted.eq(labels).sum().item()

    test_loss /= len(test_loader)
    test_acc = test_correct / test_total

    return train_loss, train_acc, test_loss, test_acc

def main():
    train_loader, test_loader = MyDataset().get_loader()
    writer = SummaryWriter('logs/ResNet18')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = resnet.Resnet18WithSoftmax().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE, weight_decay=config.WEITHT_DECAY)
    t = time.time()
    checkpoint_dir = 'checkpoint'

    fine_tuning = False
    if fine_tuning:
        model.load_state_dict(torch.load(r"checkpoint/ResNet18_Epoch_94.pth")) 
    print(f'Fine Tuning : {fine_tuning}')

    for epoch in range(config.EPOCH):
        train_loss, train_acc, test_loss, test_acc = train_and_test(model, optimizer, criterion, train_loader, test_loader, epoch)
        log = f"Epoch {epoch+1}/{config.EPOCH} - Train Loss: {train_loss:.4f} - Train Acc: {train_acc:.4f} - Test Loss: {test_loss:.4f} - Test Acc: {test_acc:.4f} - Time: {time.time() - t:.2f}s"
        print(log)
        with open_log_file(config.LOGTXT_NAME) as f:
            f.write(log + "\n")

        writer.add_scalar('Train Loss', train_loss, epoch)
        writer.add_scalar('Train Accuracy', train_acc, epoch)
        writer.add_scalar('Test Loss', test_loss, epoch)
        writer.add_scalar('Test Accuracy', test_acc, epoch)

        os.makedirs(checkpoint_dir, exist_ok=True)
        torch.save(model.state_dict(), os.path.join(checkpoint_dir,  f'ResNet18_Epoch_{epoch+1}.pth'))

    writer.close()

if __name__ == '__main__':
    main()