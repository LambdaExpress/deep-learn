import threading
from PIL import Image
import pandas as pd
import torch    
import os
import shutil
from tqdm import tqdm
from PIL import ImageFile
from my_dataset import MyDataset
import warnings
import concurrent.futures
from models import resnet18_with_softmax as resnet
from models import resnet18_with_sigmoid as resnet1
warnings.filterwarnings("ignore")
ImageFile.LOAD_TRUNCATED_IMAGES = True

class Run():
    def __init__(
            self, 
            model, 
            transform,  
            model_path, 
            input_dir, 
            output_dir, 
            threshold,
            only_good,
            xlsx_path):
        
        os.makedirs(output_dir, exist_ok=True)

        self.xlsx_path = xlsx_path
        self.only_good = only_good
        self.threshold = threshold
        self.transform = transform
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.input_img_list = os.listdir(input_dir)
        self.img_output = {}

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model : torch.nn.Module = model.to(self.device)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
    def eval_img(self, img_name : str, pbar : tqdm):
        try:
            with Image.open(os.path.join(self.input_dir,img_name)) as img:
                img = img.resize((224, 224))
                img = img.convert('RGB')
                img = self.transform(img).to(self.device)
                img = img.unsqueeze(0)
                output : torch.Tensor = self.model(img)
                pbar.set_description(f"Processing {img_name.split('.')[0]} {output.item():.3f}")
                self.add_output(img_name, output.item())
        except Exception as e:
            pass
    def eval_imgs(self):
        with tqdm(self.input_img_list, mininterval=0) as pbar, \
            torch.no_grad():
            for img_name in pbar:
                self.eval_img(img_name, pbar)
    def add_output(self, img_name, output):
        self.img_output[img_name] = output
    def save_label_to_excel(self):
        a_data = pd.DataFrame(columns=('filename', 'output'))
        for index, item in enumerate(self.img_output.items()):
            a_data.loc[index + 1] =  list(item)
        a_data.to_excel(f'{self.xlsx_path}')
    def copy_from_excel(self):
        output_dir = self.output_dir
        input_dir = self.input_dir
        good_path = os.path.join(output_dir, 'good')
        bad_path = os.path.join(output_dir, 'bad')
        df = pd.read_excel(self.xlsx_path, sheet_name='Sheet1')
        df.loc
        for index in tqdm(range(len(df)), desc = 'Copying'):
            output = df.loc[index][2]
            if float(output) >= self.threshold:
                src_path = os.path.join(input_dir, df.loc[index][1])
                dst_path = os.path.join(good_path, df.loc[index][1])
                shutil.copy(src_path, dst_path)
            elif not self.only_good:
                src_path = os.path.join(input_dir, df.loc[index][1])
                dst_path = os.path.join(bad_path, df.loc[index][1])
                shutil.copy(src_path, dst_path)

def main():
    checkpoint_dir = 'checkpoint'
    output_dir = 'output'
    input_dir = r'C:\Users\LambdaExpress\Desktop\deep learn\pixiv\37929892'
    threshold = 0.99
    only_good = True
    xlsx_dir = 'xlsx'
    
    xlsx_path = os.path.join(xlsx_dir, f'{os.path.split(input_dir)[-1]}.xlsx')
    _, test_transform = MyDataset().get_transforms()
    model_path_list = []
    output_list = []

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(xlsx_dir, exist_ok=True)

    for output_file in os.listdir(checkpoint_dir):
        if output_file.endswith('.pth'):
            model_path_list.append(os.path.join(checkpoint_dir, output_file))
            output_name = os.path.splitext(output_file)[0]
            output_list.append(output_name)

    print(f'model_path_list: {model_path_list}, output_list: {output_list}')

    for i in range(len(model_path_list)):
        run = Run(
            model       =   resnet1.Resnet18WithSigmoid(),
            transform   =   test_transform,
            model_path  =   model_path_list[i],
            input_dir   =   input_dir,
            output_dir  =   os.path.join(output_dir, output_list[i]),
            threshold   =   threshold,
            only_good   =   only_good,
            xlsx_path   =   xlsx_path,
        )
        run.eval_imgs()
        run.save_label_to_excel()
        # run.copy_from_excel()
if __name__ == "__main__":
    main()