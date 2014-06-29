# -*- coding: utf-8 -*-
#
# http://djangosnippets.org/snippets/1550/
#

from decimal import Decimal

from django.template import Library

from django.db.models import Sum

register = Library()


@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)


@register.filter
def download_transaction_sum(queryset, status_filter):
    """ Calculate total of DownloadTransaction querysets """
    if status_filter == "credited":
        # TODO: complete
        queryset = queryset.filter(received_transaction_hash="zzz")
    elif status_filter == "completed":
        queryset = queryset.filter(btc_received_at__isnull=False)
    else:
        raise RuntimeError("Unknown status filter %s" % status_filter)

    sums = queryset.aggregate(Sum('btc_amount'))
    return sums.get("btc_amount__sum") or Decimal("0")