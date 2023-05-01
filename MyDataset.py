import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.utils.data import DataLoader
import config

# 定义数据预处理方式
train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(15),
    transforms.RandomCrop((224, 224), padding=28, padding_mode='reflect'),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# 加载数据集
train_dataset = datasets.ImageFolder("data/train", transform=train_transform)
test_dataset = datasets.ImageFolder("data/test", transform=test_transform)

# 定义数据加载器
train_loader = DataLoader(train_dataset, config.BATCH_SIZE, shuffle=True, pin_memory=True)
test_loader = DataLoader(test_dataset, config.BATCH_SIZE, pin_memory=True)