# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import tatianastore.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tatianastore', '0002_auto_20141130_1709'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='downloadtransaction',
            options={'verbose_name': 'Purchase', 'verbose_name_plural': 'Purchases'},
        ),
        migrations.AddField(
            model_name='album',
            name='genre',
            field=models.IntegerField(verbose_name='Music genre', choices=[(1, 'Rock'), (2, 'Metal'), (3, 'Alternative'), (4, 'Indie'), (5, 'Electro'), (6, 'Pop'), (7, 'R&B'), (8, 'Hip Hop/Rap'), (9, 'Country/Folk'), (17, 'Gospel'), (10, 'Blues/Jazz'), (11, 'World'), (12, 'Reggae'), (14, 'Indian music'), (15, 'Afro fusion'), (16, 'Cont.African'), (13, 'Punk')], null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='description',
            field=models.TextField(verbose_name='Tagline', max_length=40, null=True, help_text='Shown in the album listing', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='album',
            name='fiat_price',
            field=models.DecimalField(verbose_name='Price', max_digits=16, default=Decimal('0'), decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='song',
            name='download_mp3',
            field=models.FileField(verbose_name='MP3 file', upload_to=tatianastore.models.filename_gen('songs/'), null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='song',
            name='fiat_price',
            field=models.DecimalField(verbose_name='Price', max_digits=16, default=Decimal('0'), decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='store',
            name='btc_address',
            field=models.CharField(verbose_name='Bitcoin address', max_length=50, null=True, default=None, blank=True, help_text='Receiving address where the purchases will be credited. If you do not have cryptocurrency wallet yet you can leave this empty - the site will keep your coins until you get your own wallet.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='store',
            name='extra_facebook_html',
            field=models.TextField(verbose_name='Facebook style codes', default='', null=True, help_text='Style the Facebook store page with CSS and HTML. Please ask your webmaster for the details.', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='store',
            name='extra_html',
            field=models.TextField(verbose_name='Store style codes', default='', null=True, help_text='Style the store page with CSS and HTML. Please ask your webmaster for the details.', blank=True),
            preserve_default=True,
        ),
    ]
