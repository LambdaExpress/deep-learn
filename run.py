from ResNet import ResNet, block
from PIL import Image
import torch
from MyDataset import transform
import os
import shutil
from tqdm import tqdm
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True # 解决图片损坏问题
class Run():
    def __init__(self, classes, model_path, input_dir="input", output_dir="output"):
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(input_dir, exist_ok=True)

        self.input_dir = input_dir
        self.input_img_list = os.listdir(input_dir)
        self.output_dir = output_dir
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = ResNet(block, [3, 4, 6, 3], 3, 2).to(self.device)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        self.classes = classes
        self.img_label = {}
    def eval(self):
        with torch.no_grad():
            for img_name in tqdm(self.input_img_list, desc="Evaluating"):
                img = Image.open(os.path.join(self.input_dir,img_name))
                img = img.convert('RGB')
                img = transform(img).to(self.device)
                img = img.unsqueeze(0)
                output = self.model(img)
                label = self.classes[torch.argmax(output).item()]
                self.img_label[img_name] = label
    def move(self, fn = shutil.move):
        for value in set(self.img_label.values()):
            os.makedirs(os.path.join(self.output_dir, value), exist_ok=True)
        for img_name, label in self.img_label.items():
            output_path = os.path.join(self.output_dir, label)
            fn(os.path.join(self.input_dir, img_name), output_path)
    

if __name__ == "__main__":
    run = Run(['bad', 'good'], r'checkpoint\ft3.pth')
    run.eval()
    run.move(shutil.copy)

