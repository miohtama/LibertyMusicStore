from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django import forms
from django.db import transaction
from django.contrib.auth import forms as auth_forms
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse

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

    def has_delete_permission(self, request, obj=None):
        return False


class DownloadTransaction(admin.ModelAdmin):

    list_display = ("uuid", "get_status", "created_at", "description", "fiat_amount")

    readonly_fields = ("store", "uuid", "created_at", "description", "btc_amount", "fiat_amount", "currency", "btc_received_at", "cancelled_at")

    fields = readonly_fields

    def get_queryset(self, request):
        qs = super(DownloadTransaction, self).get_queryset(request)

        # Store owners can only operate their own stores
        if not request.user.is_superuser:
            qs = filter_user_manageable_content(request.user, qs)
        return qs

    def has_delete_permission(self, request, obj=None):
        return False


class Store(admin.ModelAdmin):

    list_display = ("id", "name", "store_url")

    change_form_template = "admin/store_form.html"

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(Store, self).get_queryset(request)

        # Store owners can only operate their own stores
        if not request.user.is_superuser:
            qs = request.user.operated_stores
        return qs

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ("operators",)
        return super(Store, self).get_readonly_fields(request, obj)


class Song(admin.ModelAdmin):

    list_display = ('visible', 'album', 'name', "fiat_price")

    list_display_links = ("name",)

    fields = ("visible", "store", "album", "name", "fiat_price", "download_mp3", "prelisten_mp3", "prelisten_vorbis")

    readonly_fields = ("order",)

    def get_form(self, request, obj=None, **kwargs):
        # https://djangosnippets.org/snippets/1558/
        form = super(Song, self).get_form(request, obj, **kwargs)
        # form class is created per request by modelform_factory function
        # so it's safe to modifys
        if not request.user.is_superuser:
            default_store = request.user.operated_stores.first()
            form.base_fields['store'].queryset = request.user.operated_stores
            form.base_fields['store'].initial = default_store

            form.base_fields['album'].queryset = default_store.album_set.all()
            form.base_fields['album'].initial = default_store.album_set.first()

        return form

    def get_queryset(self, request):
        qs = super(Song, self).get_queryset(request)

        # Store owners can only operate their own stores
        if not request.user.is_superuser:
            qs = filter_user_manageable_content(request.user, qs)
        return qs

    def has_delete_permission(self, request, obj=None):
        return False


class SongInline(admin.TabularInline):
    model = models.Song
    fields = ("visible", "order", "name", "fiat_price", "edit")
    readonly_fields = fields
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def edit(self, obj):
        """ Song edit links in album view.
        """
        return "<a href='%s'>Edit</a>" % reverse("admin:tatianastore_song_change", args=(obj.id,))
    edit.allow_tags = True


class Album(admin.ModelAdmin):
    inlines = [SongInline]

    fields = ("visible", "store", "name", "fiat_price", "cover", "download_zip")

    def get_queryset(self, request):
        qs = super(Album, self).get_queryset(request)

        # Store owners can only operate their own stores
        if not request.user.is_superuser:
            qs = filter_user_manageable_content(request.user, qs)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        # https://djangosnippets.org/snippets/1558/
        form = super(Album, self).get_form(request, obj, **kwargs)
        # form class is created per request by modelform_factory function
        # so it's safe to modifys
        if not request.user.is_superuser:
            form.base_fields['store'].queryset = request.user.operated_stores
            form.base_fields['store'].initial = request.user.operated_stores.first()
        return form

    # https://djangosnippets.org/snippets/1053/
    class Media:
        js = (
            'https://code.jquery.com/jquery-2.0.3.min.js',
            '/static/admin/jquery-ui-1.10.4.custom.js',
            '/static/admin/menusort.js',
        )

        css = {
            'all': ('/static/admin/hide-tabularinline-name.css',),
        }

    def has_delete_permission(self, request, obj=None):
        return False


def filter_user_manageable_content(user, queryset):
    """ Limit queryset so that it only contains objects for the stores the user can manabe.
    """

    if user.is_superuser:
        # No limitations for the staff users
        return queryset
    else:
        stores = user.operated_stores.all()
        return queryset.filter(store__in=stores)


admin.site.register(models.User, User)
admin.site.register(models.DownloadTransaction, DownloadTransaction)
admin.site.register(models.Album, Album)
admin.site.register(models.Song, Song)
admin.site.register(models.Store, Store)
