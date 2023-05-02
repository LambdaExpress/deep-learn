from PIL import Image
import torch    
import os
import shutil
from tqdm import tqdm
from PIL import ImageFile
import torchvision.transforms as transforms
import models.resnet as models
from MyDataset import test_transform
import hashlib

ImageFile.LOAD_TRUNCATED_IMAGES = True # 解决图片损坏问题

class Run():
    def __init__(self, model, transform, classes, model_path, input_dir, output_dir):
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(input_dir, exist_ok=True)

        self.transform = transform
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.input_img_list = os.listdir(input_dir)
        self.classes = classes
        self.img_label = {}

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model : torch.nn.Module = model.to(self.device)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
    def eval(self):
        with torch.no_grad():
            pars = tqdm(self.input_img_list)
            for img_name in pars:
                img = Image.open(os.path.join(self.input_dir,img_name))
                pars.set_description(f"Processing {img_name}")
                img = img.convert('RGB')
                img = self.transform(img).to(self.device)
                img = img.unsqueeze(0)
                output = self.model(img)
                label = self.classes[torch.argmax(output).item()]
                self.img_label[img_name] = label
    def copy(self):
            for value in set(self.img_label.values()):
                os.makedirs(os.path.join(self.output_dir, value), exist_ok=True)
            for img_name, label in self.img_label.items():
                output_path = os.path.join(self.output_dir, label)
                shutil.copy(os.path.join(self.input_dir, img_name), output_path)
def sum(inputs, outputs, other_name = 'or'):

    if len(outputs) <= 1:
        raise ValueError('The number of output folders should be greater than 1.')

    os.makedirs(outputs, exist_ok=True)
    os.makedirs(os.path.join(outputs, other_name), exist_ok=True)
    # 定义一个用于存储相同文件的空列表
    same_files = {}
    # 遍历文件夹1中的所有文件，计算它们的SHA256哈希值
    for root, _, files in os.walk(inputs[0]):
        label = root.split('\\')[-1]
        pars = tqdm(files)
        for file in pars:
            pars.set_description(f'Calculating SHA256 Label {label}')
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            # 检查文件在其他文件夹中是否存在，并且SHA256哈希值是否相同
            is_exist = True
            for input in inputs[1:]:
                if not (os.path.exists(os.path.join(input + r'\\' + label, file)) and \
                hashlib.sha256(open(os.path.join(input + r'\\' + label, file), 'rb').read()).hexdigest() == file_hash):
                    is_exist = False
                    break
            if is_exist:
                same_files[file] = label

    # 复制相同的文件到另一个文件夹
    for file, label in tqdm(same_files.items(), desc='Copying files'):
        os.makedirs(os.path.join(outputs, label), exist_ok=True)
        src_file = os.path.join(inputs[0] + '\\' + label, file)
        dst_file = os.path.join(outputs + '\\' + label, file)
        shutil.copy2(src_file, dst_file)
    for intput in inputs:
        for root, _, files in os.walk(intput):
            files = list(set(files) - set(same_files.keys()))
            for file in tqdm(files, desc='Copying other files', leave=False):
                shutil.copy2(os.path.join(root, file), os.path.join(outputs + '\\' + other_name, file))

if __name__ == "__main__":
    model_path_list = []
    output_list = os.listdir('checkpoint')
    output_head = 'output'
    for i in range(0, len(output_list)):
        output_name = os.path.join(output_head, output_list[i]).split('.')[0]
        checkpoint_name = os.path.join('checkpoint', output_list[i])
        output_list[i] = output_name
        model_path_list.append(checkpoint_name)
    os.makedirs(output_head, exist_ok=True)
    print(f'model_path_list : {model_path_list}, output_list : {output_list}')

    for i in tqdm(range(0, len(model_path_list)), desc='Running'):
        run = Run(
                    models.model(),\
                    test_transform, \
                    ['bad', 'good'], \
                    model_path_list[i], \
                    r'input', \
                    output_list[i])
        run.eval()
        run.copy()
    sum(output_list, r'output.sum')

