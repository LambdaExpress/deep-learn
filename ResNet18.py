import torch
import torch.nn as nn
from torch.nn.modules.batchnorm import BatchNorm2d
import torch.nn.functional as F
#nn.Relu必须添加到nn.Module容器中才能使用，而F.ReLU则作为一个函数调用
 
'''
本文  resblk表示一个完整的残差块 h(x) = f(x) + x 
而1*1的卷积 放到ResNet18中
'''
 
class Resblk(nn.Module):
    def __init__(self,ch_in,ch_out,stride1,stride2) -> None:
        super(Resblk,self).__init__()
        self.blk = nn.Sequential(
            nn.Conv2d(ch_in,ch_out,kernel_size=3,stride=stride1,padding=1),
            nn.BatchNorm2d(ch_out),
            nn.ReLU(),
            nn.Conv2d(ch_out,ch_out,kernel_size=3,stride=stride2,padding=1),
            nn.BatchNorm2d(ch_out)
        )
        self.extra = nn.Sequential()
        #输入输出通道数不同的话
        if ch_in != ch_out:
            self.extra = nn.Sequential(             
                nn.Conv2d(ch_in,ch_out,kernel_size=1,stride=2,padding=0),
                nn.BatchNorm2d(ch_out)
            )
 
    def forward(self,x):
        out = F.relu(self.blk(x)+self.extra(x))
        return out
 
 
class ResNet18(nn.Module):
    def __init__(self, classes=2) -> None:
        super(ResNet18,self).__init__()

        self.classes = classes
 
        self.preconv = nn.Sequential(
            nn.Conv2d(3,64,kernel_size=7,stride=2,padding=3),
            nn.MaxPool2d(kernel_size=3,stride=2,padding=1)
        )
        self.conv1 = nn.Sequential(
            nn.Conv2d(64,128,kernel_size=1,stride=2,padding=0),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(128,256,kernel_size=1,stride=2,padding=0),
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(256,512,kernel_size=1,stride=2,padding=0),
        )
        #由于残差块中 是通过控制stride来降维度的，
        #因此我在设置Resblk时将stride作为参数输入，
        #参数意义: 输入通道，输出通道，残差块中第一层卷积步长，残差块中第二层卷积的步长
        self.blk1 = Resblk(64,64,1,1)
        self.blk2 = Resblk(64,64,1,1)
        self.blk3 = Resblk(64,128,2,1)
        self.blk4 = Resblk(128,128,1,1)
        self.blk5 = Resblk(128,256,2,1)
        self.blk6 = Resblk(256,256,1,1)
        self.blk7 = Resblk(256,512,2,1)
        self.blk8 = Resblk(512,512,1,1)
        #池化操作
        self.avgpool = nn.AdaptiveAvgPool2d(output_size=(1, 1))
        self.sig = nn.Sigmoid()
        #全连接层
        self.fc = nn.Linear(512, self.classes) #这里的1000是原文中对应1000个类吧
 
    def forward(self,x):
        #输入 224*224*3 输出 64*56*56
        #7*7 conv + maxpool
        x = self.preconv(x)
 
        #第一个残差块
        #输入 224*224*3 输出 64*56*56
        x = self.blk1(x)
        #第二个残差块
        #输入 64*56*56 输出 64*56*56
        x = self.blk2(x)
        #第三个残差块 + 1*1 subsample
        #输入 64*56*56 输出 128*28*28
        x = self.conv1(x) + self.blk3(x)
        #第四个残差块
        #输入 128*28*28 输出 128*28*28
        x = self.blk4(x)
        #第五个残差块 + 1*1 subsample
        #输入 128*28*28 输出 256*14*14
        x = self.conv2(x) + self.blk5(x)
        #第六个残差块
        #输入 256*14*14 输出 256*14*14
        x = self.blk6(x)
        #第七个残差块
        #输入 256*14*14 输出 512*7*7
        x = self.conv3(x) + self.blk7(x)
        #第八个残差块
        #输入 512*7*7 输出 512*7*7
        x = self.blk8(x)
        #平均池化 512*7*7-> 512*1*1
        x = self.avgpool(x)
        #Flatten 打平操作 后面俩维合并成一维
        x = x.view(x.size(0),-1) #[512,1]
        #全连接层 512,1 -> 1,1000
        x = self.fc(x)
        #激活函数
        #x = self.sig(x)
         
        return x
