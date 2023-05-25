from datetime import datetime, timedelta
import random

class DateGenerator:
    def __init__(self, start_date, end_date):
        self.start_date = datetime(start_date[0], start_date[1], start_date[2])
        self.end_date = datetime(end_date[0], end_date[1], end_date[2])
        self.global_index = 0
        self.date_list = []
        self.generate_dates()
        
    def reverse(self):
        self.date_list = self.date_list[::-1]

    def shuffle(self):
        self.date_list = random.sample(self.date_list, len(self.date_list))

    def __generate_dates(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            date_string = current_date.strftime('%Y%m%d')
            yield date_string
            current_date += timedelta(days=1)

    def get_date(self) -> str:
        self.check_index(self.global_index)
        return self.date_list[self.global_index]

    def next(self) -> None:
        self.check_index(self.global_index)
        self.global_index += 1

    def generate_dates(self) -> None:
        self.date_list = [date for date in self.__generate_dates()]

    def check_index(self, index) -> None:
        if index >= len(self.date_list):
            raise IndexError("DateGenerator index out of range")