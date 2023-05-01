import torch
import torchvision.models as models
import torch.nn as nn
import torch.optim as optim

def model() -> nn.Module:
    model = models.resnet18(pretrained=True)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2)
    model.softmax = nn.Softmax(dim=1)
    return model