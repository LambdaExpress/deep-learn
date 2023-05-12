from io import BytesIO
import requests
from spider import Spider
import os
import sys
import torch
from PIL import Image, ImageFile
import warnings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.resnet18_with_softmax import Resnet18WithSoftmax
from my_dataset import MyDataset
from pixiv_spider import PixivSpider
warnings.filterwarnings("ignore")
ImageFile.LOAD_TRUNCATED_IMAGES = True

class LikePixivSpider(PixivSpider):
    def __init__(self, 
                 session: requests.Session, 
                 model : torch.nn.Module, 
                 model_path: str, 
                 transform):
        super().__init__(session, [])
        self.transform = transform
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
    def eval(self, response: requests.Response):
        with torch.no_grad():
            img = self.get_img(response)
            img = self.transform(img).to(self.device)
            img = img.unsqueeze(0)
            output = self.model(img)
            return output[0][1].item()
    def get_img(self, response: requests.Response):
        img = Image.open(BytesIO(response.content))
        img = img.convert('RGB')
        return img
    def save_img(self, response: requests.Response, path: str):
        img = self.get_img(response)
        img.save(path)
if __name__ == '__main__':
    _, transform = MyDataset().get_transforms()
    spider = LikePixivSpider(session=requests.Session(), 
                        model=Resnet18WithSoftmax(), 
                        model_path='checkpoint/ResNet18_Epoch_11.pth',
                        transform=transform)
    response = spider.get(r'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Nanshan_Stone_Carving%2C_2018-10-27_19.jpg/2560px-Nanshan_Stone_Carving%2C_2018-10-27_19.jpg')
    threshold = 0.99
    eval_result = spider.eval(response)
    print(eval_result)