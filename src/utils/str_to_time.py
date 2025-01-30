from datetime import datetime


def str_to_time(string:str):
    return datetime.datetime.strptime(string,'%H:%M')