"""

    Public facing front.

"""

import logging

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns
from django.conf.urls import url

from .models import Album

logger = logging.getLogger(__name__)


def index(request):
    """ """

    # Get splash albums
    splash_albums = Album.objects.filter(cover__isnull=False, visible=True, fiat_price__gt=0).exclude(cover__exact='')
    splash_albums = [a for a in splash_albums if a.song_set.count() > 0]

    return render_to_response("site/index.html", locals(), context_instance=RequestContext(request))


def about(request):
    """ """
    return render_to_response("site/about.html", locals(), context_instance=RequestContext(request))


def info(request):
    """ """
    return render_to_response("site/info.html", locals(), context_instance=RequestContext(request))


def bitcoin(request):
    """ """
    return render_to_response("site/bitcoin.html", locals(), context_instance=RequestContext(request))


urlpatterns = patterns('',
    url(r'^about/$', about, name="about"),
    url(r'^info/$', info, name="info"),
    url(r'^bitcoin/$', bitcoin, name="bitcoin"),
)
