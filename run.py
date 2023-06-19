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
        self.img_output = {}

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model : torch.nn.Module = model.to(self.device)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
    def eval_tensor(self, img_path, tensor : torch.Tensor):
        output = self.model(tensor)
        self.add_output(os.path.split(img_path)[-1], output.item())
    def __process_img(self, img_path):
        try:
            img = Image.open(img_path)
            img = img.resize((224, 224))
            img = img.convert('RGB')
            img = self.transform(img).to(self.device)
            img = img.unsqueeze(0)
            return img, img_path
        except:
            return False
    def eval_imgs(self, split_threshold : int = 1000):
        imgs_path = [os.path.join(self.input_dir, name) for name in os.listdir(self.input_dir)]
        split_img_path = [imgs_path[i:i+split_threshold] for i in range(0, len(imgs_path), split_threshold)]
        pbar = tqdm(total=2 * len(imgs_path), desc='Total Process')
        for _split_img_path in split_img_path:
            img_tensors_paths = {}
            with concurrent.futures.ThreadPoolExecutor() as executor, \
                tqdm(_split_img_path, desc='Generate Tensor', leave=False) as generate_pbar:
                futures = [executor.submit(self.__process_img, img_path) 
                           for img_path in _split_img_path]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    generate_pbar.update()
                    pbar.update()
                    if not result:
                        continue
                    img_tensor, img_path = result
                    img_tensors_paths[img_tensor] = img_path
            with torch.no_grad(), \
                tqdm(img_tensors_paths.keys(), leave=False, desc='Process Tensor') as tensor_pbar:
                for tensor in tensor_pbar:
                    self.eval_tensor(img_tensors_paths[tensor], tensor)
                    pbar.update()
    def add_output(self, img_name, output):
        self.img_output[img_name] = output
    def save_label_to_excel(self):
        a_data = pd.DataFrame(columns=('filename', 'output'))
        for index, item in tqdm(enumerate(self.img_output.items()), leave=False, desc='Saving'):
            a_data.loc[index + 1] =  list(item)
        a_data.to_excel(f'{self.xlsx_path}')
    def copy_from_excel(self):
        output_dir = self.output_dir
        input_dir = self.input_dir
        good_path = os.path.join(output_dir, 'good')
        bad_path = os.path.join(output_dir, 'bad')
        os.makedirs(good_path, exist_ok=True)
        if not self.only_good:
            os.makedirs(bad_path, exist_ok=True)
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
    input_dir = r'pixiv\2342360'
    threshold = 0.8
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