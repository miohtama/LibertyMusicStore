# -*- coding: utf-8 -*-
#
# http://djangosnippets.org/snippets/1550/
#


from django.template import Library

register = Library()


@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)