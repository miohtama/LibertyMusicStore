from django.conf import settings

from tatianastore import models

models.Album.objects.filter(fiat_price=settings.OLD_DEFAULT_ALBUM_PRICE).update(fiat_price=settings.DEFAULT_ALBUM_PRICE)
models.Song.objects.filter(fiat_price=settings.OLD_DEFAULT_SONG_PRICE).update(fiat_price=settings.DEFAULT_SONG_PRICE)
