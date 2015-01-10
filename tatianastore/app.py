import os
import sys
import logging

from django.apps import AppConfig
from django.conf import settings


logger = logging.getLogger(__name__)


class TatianastoreConfig(AppConfig):
    name = 'tatianastore'
    verbose_name = "Liberty Music Store core"

    def ready(self):

        logger.error("Rock and roll")
        # Register signal handlers
        from tatianastore import payment