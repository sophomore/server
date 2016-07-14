from django.conf.urls import url
from main.views import MenuApi, OrderApi, PrintStatementApi, PrintReceiptApi, SalesApi, \
    SimpleStatisticApi, StatisticApi

urlpatterns = [
    url(r'^menu/$|^menu/(?P<id>\d+)/$', MenuApi.as_view(), name='menu'),
    url(r'^order/$|^order/(?P<id>\d+)/$', OrderApi.as_view(), name='order'),
    url(r'^print_statement/$|^print_statement/(?P<id>\d+)/$', PrintStatementApi.as_view(), name='print_statement'),
    url(r'^print_receipt/$|^print_receipt/(?P<id>\d+)/$', PrintReceiptApi.as_view(), name='print_receipt'),
    url(r'^sales/$', SalesApi.as_view(), name='sales'),
    url(r'^statistic/$', StatisticApi.as_view(), name='statistic'),
    url(r'^statistic/simple/$', SimpleStatisticApi.as_view(), name='statistic_simple'),
]