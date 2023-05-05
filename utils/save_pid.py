import os
from tqdm import tqdm


def add_pid(input_dir, pid_set : set):
    for _, _, files in os.walk(input_dir):
        for file in tqdm(files, desc='Saving pid', leave=False):
                pid_set.add(file.split('.')[0].split('_')[0])
def run(input_dirs):
    pid = set()
    for input_dir in input_dirs:
        add_pid(input_dir, pid)
    return pid

