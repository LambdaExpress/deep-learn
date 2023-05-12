import os
from tqdm import tqdm

class PidExtractor:
    def __init__(self, input_dirs):
        self.input_dirs = input_dirs
        self.pid_set = set()

    def extract_pid(self):
        """
        Extracts the pid from the filenames in the input directories and adds them to the pid_set.
        """
        for input_dir in self.input_dirs:
            for _, _, files in os.walk(input_dir):
                for file in tqdm(files, desc='Saving pid', leave=False):
                    pid = file.split('.')[0].split('_')[0]
                    self.pid_set.add(pid)

    def get_pid_list(self):
        """
        Returns a set of unique pids extracted from the filenames in the input directories.

        Returns:
            A set of unique pids.
        """
        self.extract_pid()
        return self.pid_set