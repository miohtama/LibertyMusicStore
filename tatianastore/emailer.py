import logging

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)


def mail_store_owner(store, subject, template, template_data):

    assert store.email

    #: Let's not bother with plain-text email anymore
    text_body = "Please open the attached HTML email"

    html_body = render_to_string(template, template_data)

    msg = EmailMultiAlternatives(subject=subject, from_email="no-reply@libertymusicstore.net",
                                 to=[store.email], body=text_body)
    msg.attach_alternative(html_body, "text/html")
    msg.send()
