"""

    Sign up form.

"""


from django import forms

from django import shortcuts
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns
from django.conf.urls import url

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from slugify import slugify

CURRENCIES = [
    ("USD", "USD"),
    ("EUR", "EUR"),
    ("GBP", "GBP"),
]


class SignupForm(forms.Form):
    """
    """

    email = forms.CharField(label="Email", required=True, help_text="We'll email you the username and the password")

    artist_name = forms.CharField(label="Artist / band name", help_text="The name used on the store")

    btc_address = forms.CharField(label="Bitcoin address",
                                  help_text="The receiving Bitcoin address where you get the payments for the purchases. You can fill in this later if you don't have Bitcoin wallet right now.",
                                  required=False)

    currency = forms.ChoiceField(label="Currency", help_text="Your local currency", choices=CURRENCIES)

    def create_user(self):
        username =
        u = User.objects.craete()

def signup(request):

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.create_user()
            return shortcuts.redirect("signup_thank_you")
    else:
        form = SignupForm()

    form.helper = FormHelper()
    form.helper.add_input(Submit('submit', 'Submit'))

    return shortcuts.render_to_response("site/signup.html", locals(), context_instance=RequestContext(request))


def thank_you(request):
    return shortcuts.render_to_response("site/signup_thank_you.html", locals(), context_instance=RequestContext(request))


urlpatterns = patterns('',
    url(r'^$', signup, name="signup"),
    url(r'^thank-you/$', thank_you, name="signup_thank_you"),
)
