import json

from django.core.cache import cache
from django.db.models.signals import post_save

from django.db.models import signals
from django.dispatch import dispatcher
from django.dispatch import receiver
from django.utils.timezone import now

from . import models


@receiver(post_save, sender=models.DownloadTransaction)
def transaction_post_save(sender, instance, signal, *args, **kwargs):
    """ Poke listeners about the new state in Redis when transactions change. """
    redis = cache.raw_client
    transaction = instance
    # transaction.uuid can be UUID() or string
    message = transaction.get_notification_message()
    redis.publish("transaction_%s" % transaction.uuid, json.dumps(message))
