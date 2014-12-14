from django.conf import settings


def extra_vars(request):
    """Expose site name to templates."""
    return dict(site_name=settings.SITE_NAME, site_currency_symbol=settings.CURRENCY_SYMBOL)
