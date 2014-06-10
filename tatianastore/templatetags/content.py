# -*- coding: utf-8 -*-
#
# http://djangosnippets.org/snippets/1550/
#


from django.template import Library

register = Library()


@register.inclusion_tag('storefront/song_controls.html')
def song_controls(content_manager, song):
    tx = content_manager.get_download_transaction(song.uuid)
    enabled = song.fiat_price > 0
    return {'tx': tx, "song": song, "enabled": enabled}


@register.inclusion_tag('storefront/album_controls.html')
def album_controls(content_manager, album):
    tx = content_manager.get_download_transaction(album.uuid)
    return {'tx': tx, "album": album}
