import logging
from decimal import Decimal

from django import http
from django import forms
from django import shortcuts
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import patterns
from django.conf.urls import url
from django.template import RequestContext
from django.forms.util import ErrorList
from django.db import transaction
from django.core.urlresolvers import reverse
from django.conf import settings

from django.shortcuts import render_to_response

from . import models
from . import zipupload


logger = logging.getLogger(__name__)


class AlbumUploadForm(forms.Form):
    """ The store owner can upload the whole album as a zip file.
    """

    album_name = forms.CharField(label="Album name", help_text="The price when the user purchases the full album.")

    album_price = forms.DecimalField(initial=Decimal("9.90"))

    song_price = forms.DecimalField(initial=Decimal("0.90"), help_text="Individual song price")

    zip_file = forms.FileField(label="Choose ZIP file from your local computer")


@staff_member_required
@transaction.non_atomic_requests
def upload_album(request):
    """ Allow the artist to upload an album to the store. """

    if request.user.is_superuser:
        # Test as superuser admin
        store = models.Store.objects.first()
    else:
        store = request.user.get_default_store()

    if request.method == "POST":
        form = AlbumUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:

                upload = form.cleaned_data["zip_file"]

                album = zipupload.upload_album(store,
                                               form.cleaned_data["album_name"],
                                               upload,
                                               form.cleaned_data["album_price"],
                                               form.cleaned_data["song_price"],
                                               )

                wizard = models.WelcomeWizard(request.user)
                wizard.set_step_status("upload_album", True)

                # JavaScript redirect to this URL
                return http.HttpResponse(reverse('admin:tatianastore_album_change', args=(album.id,)))
            except zipupload.BadAlbumContenException as e:
                # Handle bad upload content errors
                logger.error("Bad album content")
                logger.exception(e)
                errors = form._errors.setdefault("zip_upload", ErrorList())
                errors.append(unicode(e))
    else:
        form = AlbumUploadForm()

    return render_to_response("storeadmin/upload_album.html", locals(), context_instance=RequestContext(request))


@staff_member_required
def add_to_facebook(request):
    """ The page giving the button for adding the store to Facebook. """

    if request.user.is_superuser:
        # Test as superuser admin
        store = models.Store.objects.first()
    else:
        store = request.user.get_default_store()

    # Facebook signals back if the add was succesful
    added = request.GET.get("added")
    site_url = settings.SITE_URL
    store_url = reverse("store", args=(store.slug,))
    facebook_redirect_url = request.build_absolute_uri(store_url) + "?facebook=true"

    # Development mode -> the page must be accessible through
    # SSH reverse tunnel
    if settings.DEBUG:
        facebook_redirect_url = facebook_redirect_url.replace("http://localhost:8000", "http://libertymusicstore.net:9999")

    return render_to_response("storeadmin/add_to_facebook.html", locals(), context_instance=RequestContext(request))


@staff_member_required
def store_facebook_data_ajax(request):
    """ Because how Facebook works we need to play this trickery here. """


urlpatterns = patterns('',
    url(r'^upload-album/$', upload_album, name="upload_album"),
    url(r'^add-to-facebook/$', add_to_facebook, name="add_to_facebook"),
)
