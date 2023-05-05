from datetime import datetime, timedelta

class DateGenerator:
    def __init__(self, start_date, end_date):
        self.start_date = datetime(start_date[0], start_date[1], start_date[2])
        self.end_date = datetime(end_date[0], end_date[1], end_date[2])
        self.global_index = 0
        self.date_list = []
        for date in self.__generate_dates():
            self.date_list.append(date)

    def __generate_dates(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            date_string = current_date.strftime('%Y%m%d')
            yield date_string
            current_date += timedelta(days=1)
    def __call__(self) -> str:
        return self.date_list[self.global_index]
    def next(self):
        self.global_index += 1