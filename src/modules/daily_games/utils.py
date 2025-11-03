import datetime

def how_many_days_since_date(past_date: datetime.date, current_date: datetime.date):
    delta = current_date - past_date
    return delta.days


def date_after_days_passed(origin_date: datetime.date, days: int):
    days = int(days)
    return origin_date + datetime.timedelta(days=days)


