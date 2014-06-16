"""

    Customer visible parts of the store.

"""

import os
import time
import logging
import json
from decimal import Decimal
from django.contrib.auth.decorators import login_required
import datetime

from django import http
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.timezone import now
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns
from django.conf.urls import url

from . import models
from . import forms
from . import blockchain
from utils import get_session_id

logger = logging.getLogger(__name__)


def index(request):
    """ """
    return render_to_response("site/index.html", locals(), context_instance=RequestContext(request))


urlpatterns = patterns('',
#    url(r'^/$', order, name="index"),
)
