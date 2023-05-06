import pandas as pd

class LogParser:
    def __init__(self, log_file, output_file):
        self.log_file = log_file
        self.output_file = output_file
        self.df = pd.DataFrame(columns=['Epoch', 'Train Loss', 'Train Acc', 'Test Loss', 'Test Acc', 'Time'])

    def parse_log(self):
        """
        Parses the log file and stores the data in a pandas dataframe.
        """
        with open(self.log_file, 'r') as f:
            data = f.readlines()

        for line in data:
            epoch = line.split('/')[0].split()[-1]
            train_loss = line.split('Train Loss: ')[1].split()[0]
            train_acc = line.split('Train Acc: ')[1].split()[0]
            test_loss = line.split('Test Loss: ')[1].split()[0]
            test_acc = line.split('Test Acc: ')[1].split()[0]
            time = line.split('Time: ')[1].split()[0]
            self.df = self.df.append({'Epoch': epoch, 'Train Loss': train_loss, 'Train Acc': train_acc, 'Test Loss': test_loss, 'Test Acc': test_acc, 'Time': time}, ignore_index=True)

    def save_to_excel(self):
        """
        Saves the data in the pandas dataframe to an Excel file.
        """
        self.parse_log()
        self.df.to_excel(self.output_file, index=False)
if __name__ == '__main__':
    log_parser = LogParser('log.txt', 'data.xlsx')
    log_parser.save_to_excel()