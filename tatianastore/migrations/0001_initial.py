# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import tatianastore.models
import django.core.validators
import uuid
import easy_thumbnails.fields
import django.utils.timezone
from django.conf import settings
import jsonfield.fields
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')], unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=75, verbose_name='email address')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', verbose_name='staff status', default=False)),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active', default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, default=uuid.uuid4, max_length=64, editable=False)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('name', models.CharField(blank=True, max_length=80, null=True)),
                ('fiat_price', models.DecimalField(help_text='Will be automatically converted to the Bitcoin on the moment of purchase', default=Decimal('0'), decimal_places=2, verbose_name='Price in your local currency', max_digits=16, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('visible', models.BooleanField(help_text='Uncheck this to make the item disappear from your store. The site still retains the copy of this item for a while before it is permanently deleted.', verbose_name='Visible / deleted', default=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('cover', easy_thumbnails.fields.ThumbnailerImageField(blank=True, help_text='Cover art as JPEG file', null=True, upload_to=tatianastore.models.filename_gen('covers/'), verbose_name='Cover art')),
                ('download_zip', models.FileField(blank=True, help_text='A ZIP file which the user can download after he/she has paid for the full album', null=True, upload_to=tatianastore.models.filename_gen('songs/'), verbose_name='Album download ZIP')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DownloadTransaction',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('customer_email', models.CharField(blank=True, max_length=64, null=True)),
                ('session_id', models.CharField(blank=True, max_length=64, null=True)),
                ('description', models.CharField(blank=True, default='', max_length=256, editable=False)),
                ('uuid', models.CharField(blank=True, default=uuid.uuid4, max_length=64, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('currency', models.CharField(blank=True, max_length=5, null=True)),
                ('user_currency', models.CharField(blank=True, max_length=5, null=True)),
                ('btc_address', models.CharField(blank=True, max_length=50, null=True)),
                ('btc_amount', models.DecimalField(default=Decimal('0'), max_digits=16, decimal_places=8)),
                ('fiat_amount', models.DecimalField(default=Decimal('0'), max_digits=16, decimal_places=2)),
                ('payment_source', models.CharField(max_length=32)),
                ('btc_received_at', models.DateTimeField(blank=True, null=True)),
                ('manually_confirmed_received_at', models.DateTimeField(blank=True, null=True)),
                ('received_transaction_hash', models.CharField(blank=True, max_length=256, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('expired_at', models.DateTimeField(blank=True, null=True)),
                ('ip', models.IPAddressField(blank=True, null=True)),
                ('credited_at', models.DateTimeField(blank=True, null=True)),
                ('credit_transaction_hash', models.CharField(blank=True, max_length=256, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DownloadTransactionItem',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('transaction', models.ForeignKey(to='tatianastore.DownloadTransaction')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, default=uuid.uuid4, max_length=64, editable=False)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('name', models.CharField(blank=True, max_length=80, null=True)),
                ('fiat_price', models.DecimalField(help_text='Will be automatically converted to the Bitcoin on the moment of purchase', default=Decimal('0'), decimal_places=2, verbose_name='Price in your local currency', max_digits=16, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('visible', models.BooleanField(help_text='Uncheck this to make the item disappear from your store. The site still retains the copy of this item for a while before it is permanently deleted.', verbose_name='Visible / deleted', default=True)),
                ('download_mp3', models.FileField(blank=True, help_text='The downloaded content how the user gets it after paying for it.', null=True, upload_to=tatianastore.models.filename_gen('songs/'), verbose_name='MP3 file')),
                ('prelisten_mp3', models.FileField(blank=True, help_text='For Safari and IE browsers. Leave empty: This will be automatically generated from uploaded song.', null=True, upload_to=tatianastore.models.filename_gen('prelisten/'), verbose_name='Prelisten clip MP3 file')),
                ('prelisten_vorbis', models.FileField(blank=True, help_text='For Chrome and Firefox browsers. Leave empty: This will be automatically generated from uploaded song.', null=True, upload_to=tatianastore.models.filename_gen('prelisten/'), verbose_name='Prelisten clip Ogg Vorbis file')),
                ('duration', models.FloatField(blank=True, null=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('album', models.ForeignKey(blank=True, help_text='On which album this song belongs to. Leave empty for an albumless song. (You can reorder the songs when you edit the album after uploading the songs.)', to='tatianastore.Album', null=True, verbose_name='Album')),
            ],
            options={
                'ordering': ('order', '-id'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('name', models.CharField(blank=True, max_length=80, null=True)),
                ('currency', models.CharField(help_text='Currency code for your local currency which you user to price your albums and songs', max_length=5, verbose_name='Currency', default='USD')),
                ('store_url', models.URLField(help_text='Link to home page or Facebook page', verbose_name='Homepage')),
                ('btc_address', models.CharField(blank=True, help_text='Receiving address where the purchases will be credited. If you do not have Bitcoin wallet yet you can leave this empty - the site will keep your coins until you get your own wallet.', max_length=50, default=None, null=True, verbose_name='Bitcoin address')),
                ('extra_html', models.TextField(blank=True, help_text='Style your shop with extra HTML code placed for the site embed &ltiframe&gt. Please ask your webmaster for the details. This can include CSS &lt;style&gt; tag for the formatting purposes.', null=True, verbose_name='Store styles code', default='')),
                ('extra_facebook_html', models.TextField(blank=True, help_text='Style your shop with extra HTML code placed on the shop when it is on a Facebook page.', null=True, verbose_name='Facebook styles code', default='')),
                ('facebook_data', jsonfield.fields.JSONField(default={}, verbose_name='Facebook page info')),
                ('operators', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='operated_stores')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='song',
            name='store',
            field=models.ForeignKey(to='tatianastore.Store'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='downloadtransaction',
            name='store',
            field=models.ForeignKey(to='tatianastore.Store', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='store',
            field=models.ForeignKey(to='tatianastore.Store'),
            preserve_default=True,
        ),
    ]
