from PIL import Image
import torch    
import os
import shutil
from tqdm import tqdm
from PIL import ImageFile
from my_dataset import MyDataset
import warnings
from models import resnet18_with_softmax as resnet
warnings.filterwarnings("ignore")
ImageFile.LOAD_TRUNCATED_IMAGES = True

class Run():
    def __init__(
            self, 
            model, 
            transform, 
            classes, 
            model_path, 
            input_dir, 
            output_dir, 
            threshold,
            only_good):
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(input_dir, exist_ok=True)

        self.only_good = only_good
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
            for img_name, label in tqdm(self.img_label.items(), desc='Copying'):
                if self.only_good and label != self.classes[1]:
                    continue
                output_path = os.path.join(self.output_dir, label)
                shutil.copy(os.path.join(self.input_dir, img_name), output_path)
    def set_label(self, img_name, output, threshold):
        if output[0][1] >= threshold:
            self.img_label[img_name] = self.classes[1]
        else:
            self.img_label[img_name] = self.classes[0]
def main():
    checkpoint_dir = 'checkpoint'
    output_dir = 'output'
    input_dir = 'input'
    classes = ['bad', 'good']
    threshold = 0.99
    only_good = True
    _, test_transform = MyDataset().get_transforms()

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
            model       =   resnet.Resnet18WithSoftmax(),
            transform   =   test_transform,
            classes     =   classes,
            model_path  =   model_path_list[i],
            input_dir   =   input_dir,
            output_dir  =   os.path.join(output_dir, output_list[i]),
            threshold   =   threshold,
            only_good   =   only_good,
        )
        run.eval()
        run.copy()
if __name__ == "__main__":
    main()