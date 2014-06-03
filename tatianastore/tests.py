from decimal import Decimal
import datetime
import random
import os

from mock import patch

from django.utils import timezone
from django.test import TestCase

from . import models


class FoobarTestCase(TestCase):
    """ Test it. """

    def setUp(self):
        models.User.objects.all().delete()
        models.Transaction.objects.all().delete()
