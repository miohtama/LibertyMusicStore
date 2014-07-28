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

    # Populate CSS classes for the welcome wizard steps
    wizard = models.WelcomeWizard(user)
    step_class = {}
    for step, status in wizard.get_step_statuses().items():
        step_class[step] = "step-done" if status else "step-require"
    return locals()
