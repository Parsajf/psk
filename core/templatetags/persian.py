from django import template

register = template.Library()


@register.filter
def fa_digits(value):
    return str(value).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))
