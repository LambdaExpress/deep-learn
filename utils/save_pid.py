import os
from tqdm import tqdm

def save_pid(input_dir, output_file):
    for _, _, files in os.walk(input_dir):
        for file in tqdm(files, desc='Saving pid', leave=False):
            with open(output_file, 'a') as f:
                f.writelines(file.split('.')[0].split('_')[0] + '\n')
def run(input_dirs, output_file):
    if os.path.exists(output_file):
        os.remove(output_file)
    for input_dir in input_dirs:
        save_pid(input_dir, output_file)

