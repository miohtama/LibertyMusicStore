from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django import forms
from django.db import transaction
from django.contrib.auth import forms as auth_forms
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator

from . import models


csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class UserCreationForm(auth_forms.UserCreationForm):

    class Meta:
        model = models.User
        fields = ("username",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        # import ipdb; ipdb.set_trace()
        username = self.cleaned_data["username"]
        try:
            models.User._default_manager.get(username=username)
        except models.User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class UserChangeForm(auth_forms.UserChangeForm):

    class Meta:
        model = models.User


class User(UserAdmin):
    """ Override the default user admin to use custom forms. """
    form = UserChangeForm
    add_form = UserCreationForm


class Transaction(admin.ModelAdmin):
    pass


class Artist(admin.ModelAdmin):
    pass


class Song(admin.ModelAdmin):
    pass


class Album(admin.ModelAdmin):
    pass


from django.contrib.auth.models import Group as _Group
from django.contrib.auth.models import User as _User
admin.site.unregister(_Group)
#admin.site.unregister(_User)

admin.site.register(models.User, User)
admin.site.register(models.Transaction, Transaction)
admin.site.register(models.Album, Album)
admin.site.register(models.Song, Song)
admin.site.register(models.Artist, Artist)
