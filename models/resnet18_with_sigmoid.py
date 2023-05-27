import torchvision.models as models
import torch.nn as nn

class Resnet18WithSigmoid(nn.Module):
    def __init__(self):
        super(Resnet18WithSigmoid, self).__init__()
        self.model = models.resnet18(pretrained=True)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.model(x)
        x = self.sigmoid(x)
        return x