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
import tempfile

import eyed3

from django.conf import settings

from . import models
from . import tasks

logger = logging.getLogger(__name__)


class BadAlbumContenException(Exception):
    pass


def upload_song(album, original_fname, data, order):
    """
    """

    if type(original_fname) == str:
        original_fname = original_fname.decode("utf-8")

    # Extract ID3 title for the song
    # eye3d can only operate on files, not streams
    with tempfile.NamedTemporaryFile(suffix=".mp3") as file_:
        file_.write(data)
        info = eyed3.load(file_.name)
        if not info:
            raise BadAlbumContenException(u"Could not extract MP3 info from %s orignal filename %s" % (file_.name, original_fname))

        title = info.tag.title

    if not title:
        raise BadAlbumContenException(u"The MP3 file %s did not have ID3 title tag set" % original_fname)

    song = models.Song.objects.create(store=album.store, album=album, name=title)

    normalized = "%d-%s-%d-%s.mp3" % (album.id, slugify.slugify(album.name), song.id, slugify.slugify(song.name))
    logger.info("Setting song download_mp3 to %s", normalized)
    outf = os.path.join(settings.MEDIA_ROOT, "songs", normalized)
    f = open(outf, "wb")
    f.write(data)
    f.close()

    song.price = Decimal("1.00")
    song.download_mp3.name = os.path.join("songs", normalized)
    song.order = order
    song.save()


    # Create background tasks for doing prelisten versions
    tasks.generate_prelisten(song.id)


def upload_cover(album, data):
    """
    """

    #: Todo check this is a legal image file
    normalized = "%d-%s-cover.jpg" % (album.id, slugify.slugify(album.name))
    logger.info("Setting album cover to %s", normalized)
    outf = os.path.join(settings.MEDIA_ROOT, "covers", normalized)
    f = open(outf, "wb")
    f.write(data)
    f.close()

    album.cover.name = os.path.join("covers", normalized)
    album.save()


def upload_album(store, name, zip_file):
    """ Process an album uploaded as a zip file. """

    songs = []
    cover = None

    # Create the album
    album = models.Album.objects.create(name=name, store=store)
    album.fiat_price = Decimal("9.90")

    # Set the album content as the zip
    normalized = "%d-%s-%d-%s.zip" % (store.id, slugify.slugify(store.name), album.id, slugify.slugify(album.name))
    logger.info("Setting album download_zip to %s", normalized)
    album_outf = os.path.join(settings.MEDIA_ROOT, "albums", normalized)
    shutil.copy(zip_file, album_outf)
    album.download_zip.name = os.path.join("albums", normalized)
    album.save()

    # Copy the zip file as is to album content

    with ZipFile(zip_file, 'r') as zip:
        for info in zip.infolist():
            print info.filename

            fname = info.filename.lower()

            if fname.startswith("_"):
                # Some OSX Finder created metadata
                continue

            if fname.endswith(".mp3"):
                songs.append(fname)
            elif fname.endswith(".jpg") or fname.endswith(".jpeg"):
                cover = fname

        # Copy each of the songs to the
        if not cover:
            raise BadAlbumContenException("Zip file did not contain cover.jpg file")

        if not songs:
            raise BadAlbumContenException("Zip file did not contain any MP3 files")

        # Sort songs to alphabetic order (assume 01-xxx, 02-xxx prefix)
        songs = sorted(songs)

        order = 0
        for s in songs:
            data = zip.read(s)
            upload_song(album, s, data, order)
            order += 1
