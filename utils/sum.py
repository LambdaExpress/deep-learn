import os
import shutil
import hashlib
from tqdm import tqdm
def sum(inputs, output, other_name='or'):
    if len(inputs) <= 1:
        raise ValueError('The number of inputs folders should be greater than 1.')

    os.makedirs(output, exist_ok=True)
    os.makedirs(os.path.join(output, other_name), exist_ok=True)

    same_files = {}

    for root, _, files in os.walk(inputs[0]):
        label = os.path.basename(root)
        if label in inputs[0]:
            continue
        pars = tqdm(files, desc=f'Calculating SHA256 Label {label}', )
        for file in pars:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            is_exist = True
            for input in inputs[1:]:
                input_file_path = os.path.join(input, label, file)
                if not (os.path.exists(input_file_path) and
                        hashlib.sha256(open(input_file_path, 'rb').read()).hexdigest() == file_hash):
                    is_exist = False
                    break

            if is_exist:
                same_files[file] = label

    same_files_items = same_files.items()

    for file, label in tqdm(same_files_items, desc='Copying files'):
        os.makedirs(os.path.join(output, label), exist_ok=True)
        src_file = os.path.join(inputs[0], label, file)
        dst_file = os.path.join(output, label, file)
        shutil.copy2(src_file, dst_file)

    for input in inputs:
        if input == inputs[0]:
            continue

        for root, _, files in os.walk(input):
            files = set(files) - set(same_files.keys())
            for file in tqdm(files, desc='Copying other files', leave=False):
                dst_file = os.path.join(output, other_name, file)
                if not os.path.exists(dst_file):
                    shutil.copy2(os.path.join(root, file), dst_file)
