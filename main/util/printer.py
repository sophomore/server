from datetime import datetime

import os
from django.db.models import Count
from django.utils import timezone
from main.models import OrderMenu, MenuAttribute


def print_statement(order):
    def get_order_menu_string(order_menu):
        result = '\x1d\x21\x11%s\x09%s\n\x1d\x21\x00' % (order_menu.menu.name, order_menu.get_price())
        for attribute in order_menu.attributes.all():
            result += '  ㄴ%s\n\n' % attribute.name
        return result

    def get_statement_string(time, order_menu_list_string):
        outstring = '\x1B\x44\x22\x00'
        outstring += '                                           \n'
        outstring += '                                           \n'
        outstring += '================전     표================\n\n'
        outstring += '주문:' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n'
        outstring += '----------------------------------------\n'
        outstring += '메    뉴\x09수량\n'
        outstring += '----------------------------------------\n'
        outstring += '' + order_menu_list_string
        outstring += '----------------------------------------\n\n\n\n'
        outstring += '                                        \n'
        outstring += '                                        \n'
        outstring += '                                        \n'
        outstring += '\x1bm'

    order_menu_list_string = '\x1B\x44\x21\x00'
    for order_menu in order.ordermenu_set.all():
        order_menu_list_string += get_order_menu_string(order_menu)

    f2 = open('./statement', 'w+', encoding="euc-kr")
    print('                                            \n', file=f2)  # TODO: 뭐 때문에 이거 했는지 이유 찾아서 주석 추가
    print(get_statement_string(timezone.now(), order_menu_list_string), file=f2)
    f2.close()

    os.system('lpr -P RECEIPT_PRINTER statement')


def print_receipt(order):
    def get_order_menu_string(data):
        return '  %s\x09  %d\x09%s\x09%s\n' % \
               (data.menu.name.partition('(수정')[0][:9], data.count,
                format('%,d', data.price), format('%,d', data.get_price()))

    def get_menu_attribute_string(data):
        return '  %s\x09  %d\x092500\x09%s\n' % (data.name, data.count, format('%,d', data.price * data.count))

    def get_receipt_string(time, order_menu_list_string):
        output = '                                          \n'
        output += '                                          \n'
        output += '상 호 명: 송호성 쉐프의 돈까스\n\x1b\x44\x11\x19\x22\x00'
        output += '등록번호: 134-31-16828\n'
        output += '대    표: 송호성\n'
        output += '전화번호: 031-480-4595\n'
        output += '주    소: 경기 안산시 상록구 사동 1165번지\n\n'
        output += '주문:' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n'
        output += '-----------------------------------------\n'
        output += '  상 품 명\x09수 량\x09단 가\x09금 액\n'
        output += '-----------------------------------------\n'
        output += '' + order_menu_list_string
        output += '-----------------------------------------\n'
        output += '                                         \n'
        output += '                                         \n'
        output += '                                         \n\n\n\n'
        output += '\x1B\x40\x1bm'

    order_menu_list_string = '\x1b\x44\x11\x19\x22\x00'

    for each in order.ordermenu_set.annotate(count=Count('menu')).all():
        order_menu_list_string += get_order_menu_string(each)

    for each in MenuAttribute.objects.filter(ordermenu__in=order.ordermenu_set.all()) \
            .annotate(count=Count('ordermenu_set')).all():
        order_menu_list_string += get_menu_attribute_string(each)

    order_menu_list_string += u'-----------------------------------------\n'
    order_menu_list_string += u'\x1b\x61\x02합계 : ' + str(order.get_price()) + '     \n\x1b\x61\x00'

    f1 = open('./receipt', 'w+', encoding="euc-kr")
    print(get_receipt_string(timezone.now(), order_menu_list_string), file=f1)
    f1.close()

    os.system('lpr -P RECEIPT_PRINTER receipt')
