import os
import random
import shutil
import sys
import time
from tqdm import tqdm
import torchvision.transforms as transforms
from PIL import Image

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

    def split_images(self):
        # Create directories if they do not exist

        for t in tqdm(self.types, desc="Splitting"):
            images = os.listdir(os.path.join(self.data_dir, t))
            test_images = random.sample(images, int(len(images) * self.split_ratio))
            for image in test_images:
                src_path = os.path.join(self.data_dir, t, image)
                dst_path = os.path.join(self.test_dirs[t], image)
                shutil.copy(src_path, dst_path)
            train_images = [i for i in images if i not in test_images]
            for image in train_images:
                src_path = os.path.join(self.data_dir, t, image)
                dst_path = os.path.join(self.train_dirs[t], image)
                shutil.copy(src_path, dst_path)

    def clear_images(self):
        for t in tqdm(self.types, desc="Clearing"):
            train_images = os.listdir(self.train_dirs[t])
            test_images = os.listdir(self.test_dirs[t])
            for image in train_images:
                os.remove(os.path.join(self.train_dirs[t], image))
            for image in test_images:
                os.remove(os.path.join(self.test_dirs[t], image))

    def resize(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
            ])
            img = transform(img)
            return img
        except Exception as e:
            print('Error:{} - {}'.format(image_path, e))
            return None

if __name__ == '__main__':
    data_dir = 'dataset'
    train_dir = 'data/train'
    test_dir = 'data/test'
    split_ratio = 0.25

    splitter = ImageSplitter(data_dir, train_dir, test_dir, split_ratio, ['bad', 'good'])
    splitter.clear_images()

    splitter.split_images()

    # Resize images
    for t in splitter.types:
        train_images = os.listdir(splitter.train_dirs[t])
        test_images = os.listdir(splitter.test_dirs[t])
        for image in tqdm(train_images, desc="Resizing train images"):
            image_path = os.path.join(splitter.train_dirs[t], image)
            img = splitter.resize(image_path)
            if img == None:
                continue
            img.save(image_path)
        for image in tqdm(test_images, desc="Resizing test images"):
            image_path = os.path.join(splitter.test_dirs[t], image)
            img = splitter.resize(image_path)
            if img == None:
                continue
            img.save(image_path)