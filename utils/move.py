import os
import random
import shutil
import sys
import time
from tqdm import tqdm
import torchvision.transforms as transforms
from PIL import Image
import concurrent.futures

class ImageSplitter:
    def __init__(self, data_dir, train_dir, test_dir, split_ratio, types):
        self.data_dir = data_dir
        self.train_dir = train_dir
        self.test_dir = test_dir
        self.split_ratio = split_ratio
        self.types = types

        self.train_dirs = {}
        self.test_dirs = {}

        for t in self.types:
            self.train_dirs[t] = os.path.join(self.train_dir, t)
            self.test_dirs[t] = os.path.join(self.test_dir, t)
        for t in self.types:
            os.makedirs(self.train_dirs[t], exist_ok=True)
            os.makedirs(self.test_dirs[t], exist_ok=True)
    def split_image(self, src_path, dst_path):
        try:
            with Image.open(src_path) as img:
                img = img.resize((224, 224))
                img.save(dst_path)
        except:
            pass
    def split_images(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor, tqdm(desc='image') as pbar:
            futures = []
            for t in tqdm(self.types, desc="Splitting"):
                images = os.listdir(os.path.join(self.data_dir, t))
                test_images = random.sample(images, int(len(images) * self.split_ratio))
                train_images = [i for i in images if i not in test_images]
                for image in test_images:
                    src_path = os.path.join(self.data_dir, t, image)
                    dst_path = os.path.join(self.test_dirs[t], image)
                    futures.append(executor.submit(self.split_image, src_path, dst_path))
                for image in train_images:
                    src_path = os.path.join(self.data_dir, t, image)
                    dst_path = os.path.join(self.train_dirs[t], image)
                    futures.append(executor.submit(self.split_image, src_path, dst_path))
            for future in concurrent.futures.as_completed(futures):
                future.result()
                pbar.update()
    def clear_images(self):
        for t in tqdm(self.types, desc="Clearing"):
            train_images = os.listdir(self.train_dirs[t])
            test_images = os.listdir(self.test_dirs[t])
            for image in train_images:
                os.remove(os.path.join(self.train_dirs[t], image))
            for image in test_images:
                os.remove(os.path.join(self.test_dirs[t], image))
    def copy(self, input_dir, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        image_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor, \
            tqdm(total=len(image_paths), leave=False) as pbar:
            futures = []
            for image_path in image_paths:
                dst_path = os.path.join(output_dir, os.path.split(image_path)[-1])
                futures.append(executor.submit(self.split_image, image_path, dst_path))
            for future in concurrent.futures.as_completed(futures):
                future.result()
                pbar.update()

if __name__ == '__main__':
    data_dir = 'dataset'
    train_dir = 'data/train'
    test_dir = 'data/test'
    split_ratio = 0.225

    splitter = ImageSplitter(data_dir, train_dir, test_dir, split_ratio, ['bad', 'good'])
    # splitter.copy('input', 'data/unlabeled')
    splitter.clear_images()
    splitter.split_images()