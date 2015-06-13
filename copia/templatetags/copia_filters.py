#coding: utf8
from django import template

register = template.Library()

@register.filter(name='convert_byte')
def convert_byte(value):
    one_mb = 1048576
    return "%*.*f" % (7, 2, float(value) / one_mb)

@register.filter(name='drop_string')
def drop_string(value):
    if len(value) > 200:
        value = value[0:200]+'...'
    return value

@register.filter(name='set_get_argument')
def set_get_argument(url,argument):
    from prospere.lib import set_get_argument as SGA
    return SGA(url,argument)

@register.filter(name='humanize_month')
def humanize_month(value):
    month = {
        '1' : 'Январь',
        '2' : 'Февраль',
        '3' : 'Март',
        '4' : 'Апрель',
        '5' : 'Май',
        '6' : 'Июнь',
        '7' : 'Июль',
        '8' : 'Август',
        '9' : 'Сентябрь',
        '10' : 'Октябрь',
        '11' : 'Ноябрь',
        '12' : 'Декабрь',
    }
    return month[str(value)]

@register.filter(name='replace_n2br')
def replace_n2br(value):
    return value.replace('\n','<br>')    

@register.filter(name='decimal2float')
def decimal2float(value):
    return str(value).replace(',','.')

