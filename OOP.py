from datetime import date, timedelta, datetime


# Represents a habit with all relevant attributes such as name, frequency,
# creation timestamps, and last check timestamps.
class Habit:
    def __init__(self, habit_name, frequency, created_date, created_time, check_date, check_time):
        self.habit_name = habit_name
        self.frequency = frequency
        self.created_date = created_date
        self.created_time = created_time
        self.check_date = check_date
        self.check_time = check_time


# Helper class to work with dates for CLI or habits
class DateHelper:

    # Return today's date as YYYY-MM-DD string
    @staticmethod
    def today():
        return date.today().isoformat()

    # Return date that is 1 day away as YYYY-MM-DD.
    @staticmethod
    def daily():
        return (date.today() + timedelta(days=1)).isoformat()

    # Return date that is 7 days away as YYYY-MM-DD
    @staticmethod
    def weekly():
        return (date.today() + timedelta(days=7)).isoformat()


# Helper class to work with time for CLI or habits
class TimeHelper:

    @staticmethod
    def now():
        return datetime.now().strftime("%H:%M")
