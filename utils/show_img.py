import os
from PIL import Image
def main():
    filename_path_dict = {}
    for dirpath, _, files in os.walk('pixiv'):
        for file in files:
            filename_path_dict[file] = os.path.join(dirpath, file)
    while True:
        name = input('输入图片名:')
        img = Image.open(filename_path_dict[name])
        img.show()
if __name__ == '__main__':
    main()