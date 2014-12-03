# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tatianastore', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='btc_address',
            field=models.CharField(default=None, blank=True, verbose_name='AppleByte address', help_text='Receiving address where the purchases will be credited. If you do not have Bitcoin wallet yet you can leave this empty - the site will keep your coins until you get your own wallet.', null=True, max_length=50),
            preserve_default=True,
        ),
    ]
