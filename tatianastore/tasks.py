import logging
from decimal import Decimal

from django.utils import timezone
from django.conf import settings

from huey.djhuey import crontab
from huey.djhuey import db_periodic_task

from . import models


logger = logging.getLogger(__name__)


@db_periodic_task(crontab(hour='*/1'))
def update_exchange_rates():
    """ Fetch new exchange rates from btcaverage. """
    from tatianastore.models import get_rate_converter
    converter = get_rate_converter()
    converter.update()
