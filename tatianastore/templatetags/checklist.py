"""

    New user task checklist

"""

from django.template import Library

from .. import models

register = Library()


@register.inclusion_tag('admin/checklist.html', takes_context=True)
def checklist(context):
    user = context["user"]
    store = user.get_default_store()
    wizar = models.WelcomeWizard(user)
    return locals()
