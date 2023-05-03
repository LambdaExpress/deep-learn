import pandas as pd
import sys
import os
# 从txt文件中读取数据
with open('log.txt', 'r') as f:
    data = f.readlines()

# 创建一个空的pandas数据框
df = pd.DataFrame(columns=['Epoch', 'Train Loss', 'Train Acc', 'Test Loss', 'Test Acc', 'Time'])

# 将数据添加到数据框中
for line in data:
    epoch = line.split('/')[0].split()[-1]
    train_loss = line.split('Train Loss: ')[1].split()[0]
    train_acc = line.split('Train Acc: ')[1].split()[0]
    test_loss = line.split('Test Loss: ')[1].split()[0]
    test_acc = line.split('Test Acc: ')[1].split()[0]
    time = line.split('Time: ')[1].split()[0]
    df = df.append({'Epoch': epoch, 'Train Loss': train_loss, 'Train Acc': train_acc, 'Test Loss': test_loss, 'Test Acc': test_acc, 'Time': time}, ignore_index=True)

# 将数据框保存为Excel文件
df.to_excel('data.xlsx', index=False)