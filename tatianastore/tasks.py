import logging
from decimal import Decimal

from django.utils import timezone
from django.conf import settings

from huey.djhuey import crontab
from huey.djhuey import db_periodic_task
from huey.djhuey import task

from . import models
from . import prelisten

logger = logging.getLogger(__name__)


@db_periodic_task(crontab(minute='59'))
def update_exchange_rates():
    """ Fetch new exchange rates from btcaverage. """
    from tatianastore.models import get_rate_converter
    converter = get_rate_converter()
    converter.update()


@task()
def generate_prelisten(song_id):
    """ Generate prelisten clips for the song on background. """
    song = models.Song.objects.get(id=song_id)
    logger.debug("Checking prelisten generation for song %s" % song)
    prelisten.create_prelisten_on_demand(song)
