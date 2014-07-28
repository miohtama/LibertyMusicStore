"""

    Public facing front.

"""

import logging

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns
from django.conf.urls import url

logger = logging.getLogger(__name__)


def index(request):
    """ """
    return render_to_response("site/index.html", locals(), context_instance=RequestContext(request))


def about(request):
    """ """
    return render_to_response("site/about.html", locals(), context_instance=RequestContext(request))


def info(request):
    """ """
    return render_to_response("site/info.html", locals(), context_instance=RequestContext(request))


def signup(request):
    """ """
    return render_to_response("site/signup.html", locals(), context_instance=RequestContext(request))


urlpatterns = patterns('',
    url(r'^about/$', about, name="about"),
    url(r'^info/$', info, name="info"),
)
