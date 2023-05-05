



# This model shouldn't be imported.



import warnings
import torch
import os
import sys
from PIL import Image
import torchvision.transforms as transforms
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore")
from models import resnet18_with_softmax as resnet

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

model = resnet.Resnet18WithSoftmax()
model = model.cuda()
model.load_state_dict(torch.load(os.path.join('checkpoint', os.listdir('checkpoint')[0])))
image = Image.open('test.png')
image = image.convert('RGB')
image = transform(image).cuda()
image.unsqueeze_(0)
model.eval()
print(model(image))