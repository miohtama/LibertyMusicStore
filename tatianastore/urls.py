import os
import sys
import logging

from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf.urls.static import static
from django.views import defaults

from . import storefront
from . import storeadmin
from . import site
from . import signup


logger = logging.getLogger(__name__)


def do_404(request):
    logger.error("Got 404 for %s", request.path)
    return defaults.page_not_found(request, template_name='404.html')


def do_400(request):
    logger.error("Got 400 for %s", request.path)
    return defaults.bad_request(request)


handler404 = 'tatianastore.urls.do_404'
handler400 = 'tatianastore.urls.do_400'

urlpatterns = patterns('',
    url(r'^$', 'tatianastore.site.index', name='index'),

    url(r'^blockchain_received/%s$' % settings.BLOCKCHAIN_WEBHOOK_SECRET, 'tatianastore.blockchain.blockchain_received', name='blockchain_received'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^store/', include(storefront)),
    url(r'^storeadmin/', include(storeadmin)),
    url(r'^site/', include(site)),
    url(r'^signup/', include(signup)),
    url(r'^registration/', include('registration.backends.default.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),

)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))

# This is a hack to make static resources to load
# when doing runsslserver testing against FB
if "runsslserver" in sys.argv:
    # XXX: Hardcoded for now for FB testing
    urlpatterns += static("/static/admin/", document_root="/Users/mikko/code/tatianastore/venv/lib/python2.7/site-packages/django/contrib/admin/static/admin")

    static_path = os.path.join(os.path.dirname(__file__), "static")
    urlpatterns += static(settings.STATIC_URL, document_root=static_path)

