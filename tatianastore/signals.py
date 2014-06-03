import json

from django.core.cache import cache
from django.db.models.signals import post_save

from django.db.models import signals
from django.dispatch import dispatcher
from django.dispatch import receiver
from django.utils.timezone import now

from . import models


@receiver(post_save, sender=models.Transaction)
def transaction_post_save(sender, instance, signal, *args, **kwargs):
    """ Poke listeners about the new state in Redis when transactions change. """
    redis = cache.raw_client
    transaction = instance
    customer = transaction.customer
    # transaction.uuid can be UUID() or string
    message = dict(transaction_uuid=unicode(transaction.uuid), status=transaction.get_status())
    redis.publish("customer_%d" % customer.id, json.dumps(message))


