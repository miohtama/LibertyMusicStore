import os
import sys

from django.apps import AppConfig
from django.conf import settings



class TatianastoreConfig(AppConfig):
    name = 'tatianastore'
    verbose_name = "Liberty Music Store core"

    def ready(self):

        # Register signal handlers
        from tatianastore import payment