from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from . import storefront
from . import site

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'tatianastore.site.index', name='index'),

    url(r'^blockchain_received/%s$' % settings.BLOCKCHAIN_WEBHOOK_SECRET, 'tatianastore.blockchain.blockchain_received', name='blockchain_received'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^store/', include(storefront)),
    url(r'^site/', include(site)),
    url(r'^accounts/', include('registration.backends.default.urls')),
)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))