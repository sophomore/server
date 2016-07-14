from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count
from main.models import Order
from main.util import dateutil


def get_simple_statistic(start, end):
    current = start
    result = dict()
    all_orders = Order.objects.filter(time__range=(datetime.combine(start.replace(day=1), start.min.time()),
                                                   datetime.combine(end.replace(day=1) + relativedelta(months=1) -
                                                                    relativedelta(days=1), end.min.time())))
    result['cash_total'] = all_orders.filter(ordermenu__pay=1).aggregate(total=Sum('price'))['total']
    result['card_total'] = all_orders.filter(ordermenu__pay=2).aggregate(total=Sum('price'))['total']
    result['service_total'] = all_orders.filter(ordermenu__pay=3).aggregate(total=Sum('price'))['total']
    result['credit_total'] = all_orders.filter(ordermenu__pay=4).aggregate(total=Sum('price'))['total']
    result['start'] = dateutil.convert_date_to_string(start)
    result['end'] = dateutil.convert_date_to_string(end)
    value = list()

    while current <= end:
        orders = Order.objects.filter(time__range=dateutil.convert_month_range(current))
        value.append(dict(
            key=current.strftime('%Y년 %m월'),
            cash_total=orders.filter(ordermenu__pay=1).aggregate(total=Sum('price'))['total'],
            card_total=orders.filter(ordermenu__pay=2).aggregate(total=Sum('price'))['total'],
            service_total=orders.filter(ordermenu__pay=3).aggregate(total=Sum('price'))['total'],
            credit_total=orders.filter(ordermenu__pay=4).aggregate(total=Sum('price'))['total']
        ))
        current = current + relativedelta(months=1)

    if value:
        result['value'] = value

    return result


def get_statistic_unit_hour(orders, menus):
    result = list()

    for hour in range(0, 24):
        item = dict()
        item['key'] = str(hour + 1) + '시'
        value = list()
        for menu in menus.filter(ordermenu__order__in=orders.filter(time__hour=hour)).annotate(count=Count('pk')):
            value.append(dict(
                value=menu.count,
                menu=menu.to_dict()
            ))
        if value:
            item['value'] = value
        result.append(item)

    return result


def get_statistic_unit_date(orders, menus, start, end):
    current = start
    result = list()

    while current <= end:
        item = dict()
        item['key'] = current.strftime('%Y년 %m월 %d일')
        value = list()
        for menu in menus.filter(ordermenu__order__in=orders.filter(time__range=dateutil.convert_date_range(current))) \
                .annotate(count=Count('pk')):
            value.append(dict(
                value=menu.count,
                menu=menu.to_dict()
            ))
        if value:
            item['value'] = value
        result.append(item)
        current = current + relativedelta(days=1)

    return result


def get_statistic_unit_day(orders, menus):
    result = list()

    for day in (2, 3, 4, 5, 6, 7, 1):
        item = dict()
        item['key'] = dateutil.convert_day_to_name(day)
        value = list()
        for menu in menus.filter(ordermenu__order__in=orders.filter(time__week_day=day)).annotate(count=Count('pk')):
            value.append(dict(
                value=menu.count,
                menu=menu.to_dict()
            ))
        if value:
            item['value'] = value
        result.append(item)

    return result


def get_statistic_unit_month(orders, menus, start, end):
    current = start
    result = list()

    while current <= end:
        item = dict()
        item['key'] = current.strftime('%Y년 %m월')
        value = list()
        for menu in menus.filter(ordermenu__order__in=orders.filter(time__range=dateutil.convert_month_range(current))) \
                .annotate(count=Count('pk')):
            value.append(dict(
                value=menu.count,
                menu=menu.to_dict()
            ))
        if value:
            item['value'] = value
        result.append(item)
        current = current + relativedelta(months=1)

    return result


def get_statistic_unit_quarter(orders, menus, start, end):
    current = start
    result = list()

    while current <= end:
        item = dict()
        item['key'] = current.strftime('%Y년 ') + str(current.month / 4 + 1) + '분기'
        value = list()
        for menu in menus.filter(ordermenu__order__in=orders.filter(time__range=dateutil.convert_month_range(current))) \
                .annotate(count=Count('pk')):
            value.append(dict(
                value=menu.count,
                menu=menu.to_dict()
            ))
        if value:
            item['value'] = value
        result.append(item)
        current = current + relativedelta(months=3)

    return result


def get_statistic_unit_year(orders, menus, start, end):
    current = start
    result = list()

    while current <= end:
        item = dict()
        item['key'] = current.strftime('%Y년')
        value = list()
        for menu in menus.filter(ordermenu__order__in=orders.filter(time__range=dateutil.convert_year_range(current))) \
                .annotate(count=Count('pk')):
            value.append(dict(
                value=menu.count,
                menu=menu.to_dict()
            ))
        if value:
            item['value'] = value
        result.append(item)
        current = current + relativedelta(days=1)

    return result
