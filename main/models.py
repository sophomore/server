from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from main.util import dateutil


def get_category_name(category_id):
    if category_id == 1:
        return '돈까스'
    elif category_id == 2:
        return '면류'
    elif category_id == 3:
        return '덮밥'
    elif category_id == 4:
        return '음료 및 스페셜'
    return ''


class Menu(models.Model):
    name = models.CharField(_('이름'), max_length=32, null=False, blank=False)
    price = models.IntegerField(_('가격'), null=False, blank=False)
    category = models.IntegerField(_('카테고리'), null=False, blank=False)
    available = models.BooleanField(_('활성화'), null=False, blank=False, default=False)

    def to_dict(self):
        return dict(
            id=self.pk,
            name=self.name,
            price=self.price,
            category=self.category,
            available=self.available
        )

    class Meta:
        verbose_name = '메뉴'
        verbose_name_plural = '메뉴'


class MenuAttribute(models.Model):
    name = models.CharField(_('이름'), max_length=32, null=False, blank=False)
    price = models.IntegerField(_('가격'), null=False, blank=False)
    available = models.BooleanField(_('활성화'), null=False, blank=False, default=False)

    def to_dict(self):
        return dict(
            id=self.pk,
            name=self.name,
            price=self.price
        )

    class Meta:
        verbose_name = '메뉴 속성'
        verbose_name_plural = '메뉴 속성'


class Order(models.Model):
    time = models.DateTimeField(_('주문 시각'), null=False, blank=True, default=timezone.now)
    price = models.IntegerField(_('금액'), null=False, blank=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.price = self.get_price()
        super(Order, self).save(force_insert, force_update, using, update_fields)

    def to_dict(self):
        result = dict()

        result['id'] = self.pk
        result['time'] = dateutil.convert_datetime_to_string(self.time)
        order_menus = list()
        for order_menu in self.ordermenu_set.all():
            order_menus.append(order_menu.to_dict())
        result['orderMenus'] = order_menus

        return result

    def get_price(self):
        price = 0
        for order_menu in self.ordermenu_set.all():
            price += order_menu.get_price()
        return price

    class Meta:
        verbose_name = '주문'
        verbose_name_plural = '주문'


class OrderMenu(models.Model):
    menu = models.ForeignKey(Menu)
    order = models.ForeignKey(Order)
    pay = models.IntegerField(_('지불 방법'), null=False, blank=False, default=4)
    attributes = models.ManyToManyField(MenuAttribute)

    def to_dict(self):
        result = dict()

        result['id'] = self.pk
        result['menu'] = self.menu.pk
        result['pay'] = self.pay
        attributes = list()
        for attr in self.attributes.all():
            attributes.append(attr.pk)
        result['attributes'] = attributes

        return result

    def get_price(self):
        price = self.menu.price
        for attribute in self.attributes.all():
            price += attribute.price
        return price

    class Meta:
        verbose_name = '주문한 메뉴'
        verbose_name_plural = '주문한 메뉴'
