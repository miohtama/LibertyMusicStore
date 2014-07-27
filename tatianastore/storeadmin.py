import logging
from decimal import Decimal

from django import forms
from django import shortcuts
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import patterns
from django.conf.urls import url
from django.template import RequestContext
from django.forms.util import ErrorList
from django.db import transaction

from django.shortcuts import render_to_response

from . import models
from . import zipupload


logger = logging.getLogger(__name__)


class AlbumUploadForm(forms.Form):
    """ The store owner can upload the whole album as a zip file.
    """

    album_name = forms.CharField(label="Album name")

    album_price = forms.DecimalField(initial=Decimal("9.90"))

    song_price = forms.DecimalField(initial=Decimal("0.90"))

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

                return shortcuts.redirect('admin:tatianastore_album_change', album.id)
            except zipupload.BadAlbumContenException as e:
                # Handle bad upload content errors
                logger.error("Bad album content")
                logger.exception(e)
                errors = form._errors.setdefault("zip_upload", ErrorList())
                errors.append(unicode(e))
    else:
        form = AlbumUploadForm()

    return render_to_response("storeadmin/upload_album.html", locals(), context_instance=RequestContext(request))


urlpatterns = patterns('',
    url(r'^upload-album/$', upload_album, name="upload_album"),
)
