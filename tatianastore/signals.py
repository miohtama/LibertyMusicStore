import json
import logging

from django.core.cache import cache
from django.db.models.signals import post_save
from django.db.models.signals import pre_save

from django.db.models import signals
from django.dispatch import dispatcher
from django.dispatch import receiver
from django.utils.timezone import now

from . import models
from . import prelisten
from . import tasks


logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.DownloadTransaction)
def transaction_post_save(sender, instance, signal, *args, **kwargs):
    """ Poke listeners about the new state in Redis when transactions change. """
    redis = cache.client.get_client(write=True)
    transaction = instance
    # transaction.uuid can be UUID() or string q
    message = transaction.get_notification_message()
    redis.publish("transaction_%s" % transaction.uuid, json.dumps(message))


@receiver(post_save, sender=models.Song)
def generate_prelisten_on_song_upload(sender, instance, **kwargs):
    """ Listen to model changes and trigger the background task to generate prelisten songs. """
    logger.info("Song changed %s" % instance)
    tasks.generate_prelisten(instance.id)
