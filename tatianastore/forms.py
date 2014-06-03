import datetime


from django import forms

from captcha.fields import ReCaptchaField

from . import models
from . import utils


class DownloadForm(forms.Form):
    """ Distributor can credit fiat. """

    email = forms.CharField(label="Your email", required=True, widget=forms.TextInput(attrs=dict(placeholder="E.g. 1122")))

    #: Which transactions this post credits
    transaction_uuid = forms.CharField(widget=forms.HiddenInput, required=True)

