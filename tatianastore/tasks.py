import logging
import time
import subprocess

from django.utils import timezone
from django.conf import settings

from huey.djhuey import crontab
from huey.djhuey import db_periodic_task
from huey.djhuey import task

from . import models
from . import prelisten
from . import creditor


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

    # Stupid workaround to let the tranasaction of web process have time to commit
    # when adding song from Django admin
    time.sleep(5)

    try:
        song = models.Song.objects.get(id=song_id)
    except models.Song.DoesNotExist:
        logger.error("Tried to generate prelisten for non-existing song %d", song_id)
        return
    logger.info("Checking prelisten generation for song %s" % song)
    prelisten.create_prelisten_on_demand(song)


@db_periodic_task(crontab(hour='1'))
def credit_stores():
    """ Credit authors for their purchased songs every 24 h"""

    # Prevent accidetal creditations on the developement server
    if settings.SITE_URL not in settings.ALLOWED_CREDIT_SITE_URLS:
        logger.error("Cannot credit store owners on dev server")
        return 0

    credited = 0
    for store in models.Store.objects.all():

        try:
            credited += creditor.credit_store(store)
        except Exception as e:
            # Allow individual store crediting fails, still keep plowing through rest of the stores
            logger.error("Could not credit store %s", store)
            logger.exception(e)

    return credited


@db_periodic_task(crontab(day='*/3'))
def backup_site():
    """Run site backup every three days.

    To run manually::

        echo "from tatianastore import tasks ; tasks.backup_site()"|python manage.py shell
    """
    try:
        subprocess.check_output(["bin/incremental-backup.bash", settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.BACKUP_ENCRYPTION_KEY, timeout=4*60*60, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        # Capture error in Sentry
        logger.error(e.output)
        raise