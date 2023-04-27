from ResNet import ResNet, block
from PIL import Image
import torch    
import os
import shutil
from tqdm import tqdm
from PIL import ImageFile
import torchvision.transforms as transforms
from ResNet18 import ResNet18
ImageFile.LOAD_TRUNCATED_IMAGES = True # 解决图片损坏问题
class Run():
    def __init__(self, model, classes, model_path, input_dir="input", output_dir="output"):
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(input_dir, exist_ok=True)

        self.input_dir = input_dir
        self.input_img_list = os.listdir(input_dir)
        self.output_dir = output_dir
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
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
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    run = Run(ResNet18(2), ['bad', 'good'], r'checkpoint\ResNet18_Epoch_100.pth')
    run.eval()
    run.move(shutil.copy)

