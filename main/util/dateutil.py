from datetime import datetime

from dateutil.relativedelta import relativedelta

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'


def convert_datetime_to_string(d, f=DATETIME_FORMAT):
    return d.strftime(f)


def convert_date_to_string(d, f=DATE_FORMAT):
    return d.strftime(f)


def convert_string_to_datetime(s, f=DATETIME_FORMAT):
    return datetime.strptime(s, f)


def convert_string_to_date(s, f=DATE_FORMAT):
    return datetime.strptime(s, f)


def convert_date_range(date):
    if not isinstance(date, datetime):
        date = convert_string_to_date(date)
    return (
        datetime.combine(date, date.min.timetz()),
        datetime.combine(date, date.max.timetz())
    )


def convert_month_range(date):
    if not isinstance(date, datetime):
        date = convert_string_to_date(date)
    date = date.replace(day=1)
    return (
        datetime.combine(date, date.min.timetz()),
        datetime.combine(date + relativedelta(months=1) - relativedelta(days=1), date.max.timetz())
    )


def convert_year_range(date):
    if not isinstance(date, datetime):
        date = convert_string_to_date(date)
    date = date.replace(month=1, day=1)
    return (
        datetime.combine(date, date.min.timetz()),
        datetime.combine(date + relativedelta(years=1) - relativedelta(days=1), date.max.timetz())
    )


def convert_day_to_name(day):
    if day == 1:
        return '일요일'
    elif day == 2:
        return '월요일'
    elif day == 3:
        return '화요일'
    elif day == 4:
        return '수요일'
    elif day == 5:
        return '목요일'
    elif day == 6:
        return '금요일'
    elif day == 7:
        return '토요일'
    return ''
