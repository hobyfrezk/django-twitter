from datetime import datetime
import pytz

def utc_now():
    return datetime.now().replace(tzinfo=pytz.utc)

def manitoba_time_now(time):
    # a tricky way to show local time from utc time.
    return time.replace(tzinfo=pytz.timezone('Etc/GMT-5'))