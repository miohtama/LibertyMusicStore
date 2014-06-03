# -*. coding: utf-8 -*-
"""

    Create some example content to be used with dev server.

"""

from decimal import Decimal

from tatianastore import models
from tatianastore.tasks import update_exchange_rates

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

# Get initial exchange rates
update_exchange_rates()