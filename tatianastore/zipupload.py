"""

    Upload album as a zip file.

    http://pymotw.com/2/zipfile/

"""

import os
from decimal import Decimal
from zipfile import ZipFile
import slugify
import shutil
import logging

from django.conf import settings

from . import models


logger = logging.getLogger(__name__)


class BadAlbumContenException(Exception):
    pass


def upload_album(store, name, zip_file):
    """ Process an album uploaded as a zip file. """

    songs = []
    cover = None

    # Create the album
    album = models.Album.objects.create(name=name, store=store)
    album.fiat_price = Decimal("9.90")

    # Copy the zip file as is to album content

    with ZipFile(zip_file, 'r') as zip:
        for info in zip.infolist():
            print info.filename

            fname = info.filename.lower()
            if fname.endswith(".mp3"):
                songs.append(fname)
            elif fname.endswith(".jpg") or fname.endswith(".jpeg"):
                cover = fname

        # Copy each of the songs to the
        if not cover:
            raise BadAlbumContenException("Zip file did not contain cover.jpg file")

        if not songs:
            raise BadAlbumContenException("Zip file did not contain any MP3 files")


    # Set the album content as the zip
    normalized = "%d-%s-%d-%s.zip" % (store.id, slugify.slugify(store.name), album.id, slugify.slugify(album.name))
    logger.info("Setting album download_zip to %s", normalized)
    album_outf = os.path.join(settings.MEDIA_ROOT, "albums", normalized)
    shutil.copy(zip_file, album_outf)
    album.download_zip.name = album_outf
    album.save()


