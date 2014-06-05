"""

    Generate prelisten clip for songs.

"""

# -*- coding: utf8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import subprocess

from django.conf import settings

FFMPEG = os.environ.get('FFMPEG') or "/usr/local/bin/ffmpeg"


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