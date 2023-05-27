import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.utils.data import DataLoader
import config
from torch.utils.data import Dataset
import os
from PIL import Image

class MyDataset:
    def __init__(self) -> None:
        self.train_transform = transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(15),
            transforms.RandomCrop((224, 224), padding=28, padding_mode='reflect'),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

        self.test_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

        # 加载数据集
        self.train_dataset = datasets.ImageFolder("data/train", transform=self.train_transform)
        self.test_dataset = datasets.ImageFolder("data/test", transform=self.test_transform)

        # 定义数据加载器
        self.train_loader = DataLoader(self.train_dataset, config.BATCH_SIZE, shuffle=True, pin_memory=True)
        self.test_loader = DataLoader(self.test_dataset, config.BATCH_SIZE, shuffle=True, pin_memory=True)
    def get_loader(self):
        return self.train_loader, self.test_loader
    def get_transforms(self):
        return self.train_transform, self.test_transform
    
class UnlabeledDataset(Dataset):
    def __init__(self, data_dir = 'data/unlabeled', transform=MyDataset().get_transforms()[0]):
        self.data_dir = data_dir
        self.transform = transform
        self.img_list = os.listdir(data_dir)

    def __len__(self):
        return len(self.img_list)
    def __getitem__(self, idx):
        img_path = os.path.join(self.data_dir, self.img_list[idx])
        img = Image.open(img_path).convert('RGB')
        if self.transform:
            img = self.transform(img)
        return img
    def get_loader(self):
        return DataLoader(self, config.BATCH_SIZE, shuffle=True,pin_memory=True)