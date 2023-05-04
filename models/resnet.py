import torchvision.models as models
import torch.nn as nn

class Resnet18WithSoftmax(nn.Module):
    def __init__(self, classes_num = 2):
        super(Resnet18WithSoftmax, self).__init__()
        self.model = models.resnet18(pretrained=True)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, classes_num)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.model(x)
        x = self.softmax(x)
        return x