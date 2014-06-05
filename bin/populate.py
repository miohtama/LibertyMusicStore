# -*. coding: utf-8 -*-
"""

    Create some example content to be used with dev server.

    echo "execfile('./bin/populate.py')" | python manage.py shell

"""

import os
import shutil
from decimal import Decimal

import eyed3
import audioread

from tatianastore import models
from tatianastore.tasks import update_exchange_rates
from tatianastore import prelisten


print ""
print "--------------------------"
print "Generating sample content"
print "--------------------------"
print ""

admin = models.User.objects.create(username="admin")
admin.is_superuser = True
admin.is_staff = True
admin.set_password("admin")
admin.save()

test_artist = models.Artist.objects.create(name="Test Artist")
test_artist.currency = "USD"
test_artist.save()

test_album = models.Album.objects.create(name="Test Album", owner=test_artist)
test_album.fiat_price = Decimal("8.90")
test_album.description = u"My very first album åäö"
test_album.save()

test_song1 = models.Song.objects.create(name="Song A", album=test_album)
test_song1.fiat_price = Decimal("0.95")
test_song1.save()
test_song2 = models.Song.objects.create(name="Song B", album=test_album)
test_song2.fiat_price = Decimal("0.50")
test_song2.save()

# Generate sample content from downloaded MP3s
# assume you can find
# sample-cd/cover.jpg
# sample-cd/1.mp3
# sample-cd/2.mp3
# ...
# and so on
#
sample_cd_path = os.path.join(os.getcwd(), "sample-cd")
if os.path.exists(sample_cd_path):
    print "Uploading sample CD content"
    test_album = models.Album.objects.create(name="Test Album 2", owner=test_artist)

    shutil.copyfile(sample_cd_path + "/cover.jpg", os.path.join(os.getcwd(), "media/covers/cover.jpg"))
    test_album.cover.name = "covers/cover.jpg"
    test_album.save()
    test_album.price = Decimal("9.90")

    for f in os.listdir(sample_cd_path):
        if not f.endswith(".mp3"):
            continue

        f2 = os.path.join(sample_cd_path, f)
        audiofile = eyed3.load(f2)

        song = models.Song.objects.create(name=audiofile.tag.title, album=test_album)

        # http://stackoverflow.com/a/10906037/315168
        shutil.copyfile(f2, os.path.join(os.getcwd(), "media/songs", f))
        song.price = Decimal("0.90")
        song.download_mp3.name = 'songs/' + f
        with audioread.audio_open(f2) as ar:
            song.duration = ar.duration / 1000.0

        song.save()

        prelisten.create_prelisten_from_upload(song)

# Get initial exchange rates
update_exchange_rates()