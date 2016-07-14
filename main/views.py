import json
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Sum
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from main.models import Menu, Order, OrderMenu, MenuAttribute
from main.util import printer, statistic
from main.util import dateutil


def create_response(success, message):
    return JsonResponse(dict(
        success=success,
        message=message
    ))


def create_success_response(message=''):
    return create_response(True, message)


def get_put_data(request):
    return {k: v[0] if len(v) == 1 else v for k, v in QueryDict(request.body).lists()}


class ApiView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ApiView, self).dispatch(request, *args, **kwargs)


class MenuApi(ApiView):
    def get(self, request, *args, **kwargs):
        result = list()
        for menu in Menu.objects.order_by('-pk').all():
            result.append(menu.to_dict())
        return JsonResponse(result, safe=False)

    def post(self, request, *args, **kwargs):
        data = request.POST

        menu = Menu()
        menu.name = data.get('name')
        menu.price = data.get('price')
        menu.category = data.get('category')
        menu.available = True
        menu.save()

        return create_success_response()

    def put(self, request, *args, **kwargs):
        data = get_put_data(request)

        try:
            menu = Menu.objects.get(pk=kwargs.get('id'))
        except ObjectDoesNotExist:
            return create_response(False, '존재하지 않는 메뉴입니다.')

        price = int(data.get('price', 0))
        if price != menu.price:
            menu.name = '%s (%s 수정)' % (menu.name, datetime.now().strftime('%Y년 %m월 %d일'))
            menu.available = False
            menu.save()
            menu = Menu(
                name=menu.name,
                price=price,
                category=menu.category,
                available=True
            )

        menu.name = data.get('name', menu.name)
        menu.category = data.get('category', menu.category)
        menu.save()

        return create_success_response()

    def delete(self, request, *args, **kwargs):
        try:
            menu = Menu.objects.get(pk=kwargs.get('id'))
        except ObjectDoesNotExist:
            return create_response(False, '존재하지 않는 메뉴입니다.')

        if menu.ordermenu_set.count() == 0:
            menu.delete()
        else:
            menu.available = False
            menu.name = '%s (%s 삭제)' % (menu.name, datetime.now().strftime('%Y년 %m월 %d일'))

        return create_success_response()


class OrderApi(ApiView):
    def get(self, request, *args, **kwargs):
        data = request.GET

        orders = Order.objects.order_by('-time')

        price = int(data.get('price', 0))
        if price > 0:
            if int(data.get('priceCriteria', 0)) == 1:
                orders = orders.filter(price__gte=price)
            elif int(data.get('priceCriteria', 0)) == 2:
                orders = orders.filter(price__lte=price)

        pay = json.loads(data.get('pay', '[]'))
        if pay:
            orders = orders.filter(ordermenu__pay__in=pay)

        if data.get('date'):
            orders = orders.filter(time__range=dateutil.convert_date_range(data.get('date')))

        menus = json.loads(data.get('menus', '[]'))
        if menus:
            orders = orders.filter(ordermenu__menu_id__in=menus)

        paginator = Paginator(orders.distinct(), 20)
        try:
            page_data = paginator.page(int(request.GET.get('page', 1)))
        except EmptyPage:
            page_data = paginator.page(paginator.num_pages)

        response = dict()
        response['count'] = orders.count()
        if page_data.has_next():
            response['next'] = page_data.next_page_number()
        if page_data.has_previous():
            response['prev'] = page_data.previous_page_number()

        result = list()
        for order in page_data.object_list:
            result.append(order.to_dict())

        response['results'] = result
        return JsonResponse(response, safe=False)

    def post(self, request, *args, **kwargs):
        data = request.POST

        order = Order()
        order.time = dateutil.convert_string_to_datetime(data.get('time'))
        order.save()

        order_menus = json.loads(data.get('orderMenus'))
        for each in order_menus:
            try:
                menu = Menu.objects.get(pk=each.get('menu'))
            except ObjectDoesNotExist:
                return create_response(False, '존재하지 않는 메뉴가 포함되어 있습니다.')

            attributes = MenuAttribute.objects.filter(pk__in=each.get('attributes'))
            if attributes.count() != len(each.get('attributes', '[]')):
                return create_response(False, '존재하지 않는 속성이 포함되어 있습니다.')

            order_menu = OrderMenu()
            order_menu.menu = menu
            order_menu.pay = each.get('pay', 4)
            order_menu.order = order
            order_menu.save()
            for attribute in attributes:
                order_menu.attributes.add(attribute)
            order_menu.save()

        order.save()

        return create_success_response()

    def put(self, request, *args, **kwargs):
        data = get_put_data(request)

        print(kwargs)
        try:
            order_menu = OrderMenu.objects.get(pk=kwargs.get('id'))
        except ObjectDoesNotExist:
            return create_response(False, '주문 정보가 존재하지 않습니다.')

        if not data.get('pay'):
            return create_response(False, '결제 방법 값이 올바르지 않습니다.')

        order_menu.pay = int(data.get('pay'))
        order_menu.save()

        return create_success_response()

    def delete(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(pk=kwargs.get('id'))
        except ObjectDoesNotExist:
            return create_response(False, '존재하지 않는 주문입니다.')

        for order_menu in order.ordermenu_set:
            order_menu.delete()

        order.delete()
        return create_success_response()


# TODO: 주문 정보 이전
class OrderManageApi(ApiView):
    pass


class PrintStatementApi(ApiView):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(pk=kwargs.get('id'))
        except ObjectDoesNotExist:
            return create_response(False, '존재하지 않는 주문입니다.')

        printer.print_statement(order)
        return create_success_response()


class PrintReceiptApi(ApiView):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(pk=kwargs.get('id'))
        except ObjectDoesNotExist:
            return create_response(False, '존재하지 않는 주문입니다.')

        printer.print_receipt(order)
        return create_success_response()


class SalesApi(ApiView):
    def get(self, request, *args, **kwargs):
        response = dict()
        date = dateutil.convert_string_to_date(request.GET.get('date'))
        response['date'] = date
        response['total'] = Order.objects.filter(time__range=dateutil.convert_date_range(date)) \
            .aggregate(total=Sum('price'))['total']

        return JsonResponse(response)


class SimpleStatisticApi(ApiView):
    def get(self, request, *args, **kwargs):
        data = request.GET

        start = dateutil.convert_string_to_date(data.get('start'))
        end = datetime.combine(dateutil.convert_string_to_date(data.get('end')), datetime.max.time())

        return JsonResponse(statistic.get_simple_statistic(start, end), safe=False)


class StatisticApi(ApiView):
    def get(self, request, *args, **kwargs):
        data = request.GET
        start = dateutil.convert_string_to_date(data.get('start'))
        end = datetime.combine(dateutil.convert_string_to_date(data.get('end')), datetime.max.time())

        orders = Order.objects.filter(time__range=(start, end))
        menus = Menu.objects
        if data.get('menus', '[]') != '[]':
            menus = menus.filter(pk__in=json.loads(data.get('menus')))

        unit = int(data.get('unit', 0))

        result = dict()
        result['unit'] = unit
        result['type'] = 2
        result['start'] = data.get('start')
        result['end'] = data.get('end')
        if unit == 1:  # 시간
            result['result'] = statistic.get_statistic_unit_hour(orders, menus)
            return JsonResponse(result, safe=False)
        elif unit == 2:  # 일
            result['result'] = statistic.get_statistic_unit_date(orders, menus, start, end)
            return JsonResponse(result, safe=False)
        elif unit == 3:  # 요일
            result['result'] = statistic.get_statistic_unit_day(orders, menus)
            return JsonResponse(result, safe=False)
        elif unit == 4:  # 달
            result['result'] = statistic.get_statistic_unit_month(orders, menus, start, end)
            return JsonResponse(result, safe=False)
        elif unit == 5:  # 분기
            result['result'] = statistic.get_statistic_unit_quarter(orders, menus, start, end)
            return JsonResponse(result, safe=False)
        elif unit == 6:  # 연
            result['result'] = statistic.get_statistic_unit_year(orders, menus, start, end)
            return JsonResponse(result, safe=False)

        return create_response(False, '입력된 정보가 올바르지 않습니다.')
