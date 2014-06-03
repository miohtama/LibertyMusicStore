from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from . import storefront

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'tatianastore.storefront.index', name='index'),
    #url(r'^about/$', 'tatianastore.views.about', name='about'),
    #url(r'^home/$', 'tatianastore.views.enter_payment', name='enter_payment'),
    #url(r'^pay/$', 'tatianastore.views.pay', name='pay'),

    url(r'^blockchain_received/$', 'tatianastore.blockchain.blockchain_received', name='blockchain_received'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^store/', include(storefront)),
    #(r'^accounts/', include('registration.backends.default.urls')),
)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))