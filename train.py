import torch
import torch.nn as nn
import torch.optim as optim
from ResNet import ResNet, block
from ResNet18 import ResNet18
from MyDataset import train_loader, test_loader
import time
from tqdm import tqdm

# 定义训练函数
def train(model : nn.Module, optimizer, criterion, train_loader):
    model.train() 
    running_loss = 0.0
    correct = 0.0
    for inputs, labels in tqdm(train_loader, leave=False, desc="Training"):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad() # 梯度清零
        outputs = model(inputs) # 前向传播
        loss = criterion(outputs, labels)# 计算损失
        loss.backward() # 反向传播
        optimizer.step() # 更新参数
        _, preds = torch.max(outputs, 1) # 预测~
        correct += torch.sum(preds == labels.data) # 统计预测正确的数量
        running_loss += loss.item() * inputs.size(0) # 统计损失
    epoch_loss = running_loss / len(train_loader.dataset) # 计算平均损失 
    epoch_acc = correct.double() / len(train_loader.dataset) # 计算平均精度
    return epoch_loss, epoch_acc

# 定义测试函数
def test(model : nn.Module, criterion, test_loader):
    model.eval()
    running_loss = 0.0
    correct = 0
    with torch.no_grad(): 
        for inputs, labels in tqdm(test_loader, leave=False, desc="Testing"):
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct += torch.sum(preds == labels.data)
    epoch_loss = running_loss / len(test_loader.dataset)
    epoch_acc = correct.double() / len(test_loader.dataset)
    return epoch_loss, epoch_acc

# 定义模型、损失函数和优化器
torch.manual_seed(3407)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ResNet(block, [3, 4, 6, 3], 3, 2)
model = model.to(device)
# model = ResNet18(2).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

from PIL import ImageFile 
ImageFile.LOAD_TRUNCATED_IMAGES = True # 解决图片损坏问题

#fine-tuning
fine_tuning = False
if fine_tuning:
    model.load_state_dict(torch.load(r"checkpoint/ft2.pth")) 
print(f'Fine Tuning : {fine_tuning}')

# 训练模型
num_epochs = 50
t = time.time()
for epoch in range(num_epochs):
    train_loss, train_acc = train(model, optimizer, criterion, train_loader)
    test_loss, test_acc = test(model, criterion, test_loader)
    print(f"Epoch {epoch+1}/{num_epochs} - Train Loss: {train_loss:.4f} - Train Acc: {train_acc:.4f} - Test Loss: {test_loss:.4f} - Test Acc: {test_acc:.4f} - Time: {time.time() - t:.2f}s")
    torch.save(model.state_dict(), f"checkpoint/ResNet50_Epoch_{epoch+1}.pth")