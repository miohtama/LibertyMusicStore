"""

    Upload album as a zip file.

    http://pymotw.com/2/zipfile/

"""

import os
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


def upload_song(album, original_fname, data, order, song_price):
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

    song.fiat_price = song_price
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


def upload_album(store, name, zip_file, album_price, song_price):
    """ Process an album uploaded as a zip file. """

    songs = []
    cover = None

    # Create the album
    album = models.Album.objects.create(name=name, store=store)
    album.fiat_price = album_price

    # Set the album content as the zip
    normalized = "%d-%s-%d-%s.zip" % (store.id, slugify.slugify(store.name), album.id, slugify.slugify(album.name))
    logger.info("Setting album download_zip to %s", normalized)

    album_outf = os.path.join(settings.MEDIA_ROOT, "albums", normalized)
    data = zip_file.read()
    # shutil.copy(zip_file, album_outf)
    # We cannot use direct, copy Django upload might be InMemoryUploadFile
    f = open(album_outf, "wb")
    f.write(data)
    f.close()

    album.download_zip.name = os.path.join("albums", normalized)
    album.save()

    # Copy the zip file as is to album content
    zip_file.seek(0)

    with ZipFile(zip_file, 'r') as zip:
        for info in zip.infolist():
            print info.filename

            fname = info.filename.lower()

            if fname.startswith("_"):
                # Some OSX Finder created metadata
                continue

            if fname.endswith(".mp3"):
                songs.append(info.filename)
            elif fname.endswith(".jpg") or fname.endswith(".jpeg"):
                cover = info.filename

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
            upload_song(album, s, data, order, song_price)
            order += 1

        upload_cover(album, zip.read(cover))

    return album