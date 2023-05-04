from PIL import Image
import torch    
import os
import shutil
from tqdm import tqdm
from PIL import ImageFile
import torchvision.transforms as transforms
from MyDataset import test_transform
import hashlib
import warnings
from models import resnet18_with_softmax as resnet
warnings.filterwarnings("ignore")
ImageFile.LOAD_TRUNCATED_IMAGES = True

class Run():
    def __init__(self, model, transform, classes, model_path, input_dir, output_dir, threshold):
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(input_dir, exist_ok=True)

        self.threshold = threshold
        self.transform = transform
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.input_img_list = os.listdir(input_dir)
        self.classes = classes
        self.img_label = {}

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
    def eval(self):
        with torch.no_grad():
            pars = tqdm(self.input_img_list)
            for img_name in pars:
                img = Image.open(os.path.join(self.input_dir,img_name))
                img = img.convert('RGB')
                img = self.transform(img).to(self.device)
                img = img.unsqueeze(0)
                output = self.model(img)
                pars.set_description(f"Processing {img_name} {output[0][1]:.3f}")
                self.set_label(img_name, output, self.threshold)
    def copy(self):
            for value in set(self.img_label.values()):
                os.makedirs(os.path.join(self.output_dir, value), exist_ok=True)
            for img_name, label in self.img_label.items():
                output_path = os.path.join(self.output_dir, label)
                shutil.copy(os.path.join(self.input_dir, img_name), output_path)
    def set_label(self, img_name, output, threshold):
        if output[0][1] >= threshold:
            self.img_label[img_name] = self.classes[1]
        else:
            self.img_label[img_name] = self.classes[0]
def sum(inputs, outputs, other_name='or'):
    if len(outputs) <= 1:
        raise ValueError('The number of output folders should be greater than 1.')

    os.makedirs(outputs, exist_ok=True)
    os.makedirs(os.path.join(outputs, other_name), exist_ok=True)

    same_files = {}

    for root, _, files in os.walk(inputs[0]):
        label = os.path.basename(root)
        if label in inputs[0]:
            continue
        pars = tqdm(files, desc=f'Calculating SHA256 Label {label}', )
        for file in pars:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            is_exist = True
            for input in inputs[1:]:
                input_file_path = os.path.join(input, label, file)
                if not (os.path.exists(input_file_path) and
                        hashlib.sha256(open(input_file_path, 'rb').read()).hexdigest() == file_hash):
                    is_exist = False
                    break

            if is_exist:
                same_files[file] = label

    same_files_items = same_files.items()

    for file, label in tqdm(same_files_items, desc='Copying files'):
        os.makedirs(os.path.join(outputs, label), exist_ok=True)
        src_file = os.path.join(inputs[0], label, file)
        dst_file = os.path.join(outputs, label, file)
        shutil.copy2(src_file, dst_file)

    for input in inputs:
        if input == inputs[0]:
            continue

        for root, _, files in os.walk(input):
            files = set(files) - set(same_files.keys())
            for file in tqdm(files, desc='Copying other files', leave=False):
                dst_file = os.path.join(outputs, other_name, file)
                if not os.path.exists(dst_file):
                    shutil.copy2(os.path.join(root, file), dst_file)
def main():
    checkpoint_dir = 'checkpoint'
    output_dir = 'output'
    input_dir = 'input'
    classes = ['bad', 'good']
    threshold = 0.99
    
    model_path_list = []
    output_list = []
    
    os.makedirs(output_dir, exist_ok=True)

    for output_file in os.listdir(checkpoint_dir):
        if output_file.endswith('.pth'):
            model_path_list.append(os.path.join(checkpoint_dir, output_file))
            output_name = os.path.splitext(output_file)[0]
            output_list.append(output_name)

    print(f'model_path_list: {model_path_list}, output_list: {output_list}')

    for i in range(len(model_path_list)):
        run = Run(
            resnet.Resnet18WithSoftmax(),
            test_transform,
            classes,
            model_path_list[i],
            input_dir,
            os.path.join(output_dir, output_list[i]),
            threshold
        )
        run.eval()
        run.copy()
    # sum(output_list, r'output.sum')

if __name__ == "__main__":
    main()