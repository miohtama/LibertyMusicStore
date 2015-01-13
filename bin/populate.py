# -*. coding: utf-8 -*-
"""

    Create some example content to be used with dev server.

    echo "execfile('./bin/populate.py')" | python manage.py shell

"""

import os
import shutil
from decimal import Decimal

import stagger

from tatianastore import models
from tatianastore.tasks import update_exchange_rates
from tatianastore import prelisten



print("")
print("--------------------------")
print("Generating sample content")
print("--------------------------")
print("")

models.update_initial_groups()

if models.User.objects.filter(username="admin").count() == 0:
   admin = models.User.objects.create(username="admin")
   admin.is_superuser = True
   admin.is_staff = True
   admin.set_password("admin")
   admin.save()

test_artist = models.Store.objects.create(name="Test Store")
test_artist.currency = "USD"
test_artist.store_url = "http://localhost:8000/store/test-store/"
test_artist.save()

test_album = models.Album.objects.create(name="Test Album", store=test_artist)
test_album.fiat_price = Decimal("8.90")
test_album.description = u"My very first album åäö"
test_album.save()

test_song1 = models.Song.objects.create(name="Song A", album=test_album, store=test_artist)
test_song1.fiat_price = Decimal("0.95")
test_song1.save()

test_song2 = models.Song.objects.create(name="Song B", album=test_album, store=test_artist)
test_song2.fiat_price = Decimal("0.50")
test_song2.save()

# Song without an album
test_song3 = models.Song.objects.create(name="Song C", store=test_artist)
test_song3.fiat_price = Decimal("0.50")
test_song3.save()


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
    print("Uploading sample CD content")
    test_album = models.Album.objects.create(name="Test Album 2", store=test_artist)

    shutil.copyfile(sample_cd_path + "/cover.jpg", os.path.join(os.getcwd(), "media/covers/cover.jpg"))
    shutil.copyfile(sample_cd_path + "/album.zip", os.path.join(os.getcwd(), "media/songs/album.zip"))
    test_album.cover.name = "covers/cover.jpg"
    test_album.download_zip.name = "songs/album.zip"
    test_album.fiat_price = Decimal("9.90")
    test_album.save()

    for f in os.listdir(sample_cd_path):
        if not f.endswith(".mp3"):
            continue

        f2 = os.path.join(sample_cd_path, f)

        info = stagger.read_tag(f2)

        song = models.Song.objects.create(name=info.title, album=test_album, store=test_artist)

        # http://stackoverflow.com/a/10906037/315168
        shutil.copyfile(f2, os.path.join(os.getcwd(), "media/songs", f))
        song.fiat_price = Decimal("0.90")
        song.download_mp3.name = 'songs/' + f

        # Fake durations
        song.duration = 61.5

        song.save()

        prelisten.create_prelisten_from_upload(song)

# Get initial exchange rates
update_exchange_rates()
