# 数据集处理
```
mkdir dataset
mkdir dataset/<labels>
mkdir data
mv <imgs_path> dataset
python util/move.py
```

# 训练&验证
```
python train
```

# 推理
配置run.py文件，将创建并将图片移动到"input"、将模型移动到"ckeckpoint".
```
mv <imgs_path> input
mv <model_path> checkpoint
```
然后
```
python run.py
```
