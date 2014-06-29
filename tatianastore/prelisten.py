"""

    Generate prelisten clip for songs.

"""

# -*- coding: utf8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import time
import subprocess
import logging

from django.conf import settings

FFMPEG = os.environ.get('FFMPEG') or "/usr/local/bin/ffmpeg"


logger = logging.getLogger(__name__)


def create_prelisten_ogg(mp3, ogg, start, duration):
    """
    Run en-code for a single file

    Do 48 kbit files for prelisten.
    """
    cmdline = [ FFMPEG, '-y', '-i', mp3, '-acodec', 'libvorbis', '-ar', '22050', '-ac', '1', '-ab', '48000', "-ss", start, "-t", duration, ogg ]
    return subprocess.call(cmdline)


def create_prelisten_aac(mp3, aac):
    """
    Run en-code for a single file

    Do 48 kbit files for prelisten.
    """
    cmdline = [ FFMPEG, '-y', '-i', mp3, '-acodec', 'libfaac', '-ar', '22050', '-ac', '1', '-ab', '48000', aac ]
    return subprocess.call(cmdline)


def create_prelisten_mp3(mp3, mp3_out, start, duration):
    """
    Run en-code for a single file

    Do 48 kbit files for prelisten.

    Limiting duration: http://stackoverflow.com/questions/6896490/how-to-set-a-videos-duration-in-ffmpeg
    """

    cmdline = [FFMPEG, '-y', '-i', mp3, '-ar', '22050', '-ac', '1', '-ab', '48000', "-ss", start, "-t", duration, mp3_out]
    return subprocess.call(cmdline)


def create_prelisten_from_upload(song, start=10, duration=30):
    """ Create and save prelistened version of the song.
    """

    logger.info("Starting prelisten production for song %d" % song.id)

    mp3 = song.download_mp3.file.name

    # convert for command line
    start = str(start)
    duration = str(duration)

    f = "prelisten-%d.mp3" % song.id
    outf = os.path.join(settings.MEDIA_ROOT, "prelisten", f)
    create_prelisten_mp3(mp3, outf, start, duration)
    song.prelisten_mp3.name = "prelisten/" + f

    f = "prelisten-%d.ogg" % song.id
    outf = os.path.join(settings.MEDIA_ROOT, "prelisten", f)
    create_prelisten_ogg(mp3, outf, start, duration)
    song.prelisten_vorbis.name = "prelisten/" + f

    song.save()


def create_prelisten_on_demand(song):
    """ Create prelisten clips only if the song MP3 content has changed.
    """

    assert song
    logger.info("Checking need for prelisten production for song %d", song.id)

    if not song.download_mp3:
        # No need to generate the field is empty
        return

    f = "prelisten-%d.mp3" % song.id
    outf = os.path.join(settings.MEDIA_ROOT, "prelisten", f)
    mp3 = song.download_mp3.file.name

    if not os.path.exist(mp3):
        logger.warn("The MP3 did not exist when tried to start creating prelisten %s", mp3)
        return

    if os.path.exists(outf):
        # Check modification time of the upload versus prelisten
        prelisten_mod_time = os.path.getmtime(outf)
        upload_mod_time = os.path.getmtime(mp3)

        logger.info("Checking if the existing prelisten needs to be overwritten. Upload %f prelisten %f", upload_mod_time, prelisten_mod_time)

        if upload_mod_time > prelisten_mod_time:
            create_prelisten_from_upload(song)
    else:
        # Fresh Song created
        create_prelisten_from_upload(song)
