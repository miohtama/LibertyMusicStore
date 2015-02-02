from decimal import Decimal
from PIL import Image
from six import StringIO

import magic

from django.forms import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from .models import get_rate_converter


def ensure_safe_user_image(image):
    """ Perform various checks to sanitize user uploaded image data.

    Checks that image was valid header, then

    :param: InMemoryUploadedFile instance (Django form field value)

    :raise: ValidationError in the case the image content has issues
    """

    if not image:
        return

    assert isinstance(image, InMemoryUploadedFile), "Image rewrite has been only tested on in-memory upload backend"

    # Make sure the image is not too big, so that PIL trashes the server
    if image:
        if image._size > 4*1024*1024:
            raise ValidationError("Image file too large - the limit is 4 megabytes")

    # Then do header peak what the image claims
    image.file.seek(0)
    try:
        mime = magic.from_buffer(image.file.getvalue(), mime=True)
        if mime not in ("image/png", "image/jpeg"):
            raise ValidationError("Image is not valid. Please upload a JPEG or PNG image.")
    except magic.MagicException:
        # System magic files could not be loaded
        mime = "image/jpeg"
        if not settings.DEBUG:
            raise

    doc_type = mime.split("/")[-1].upper()

    # Read data from cStringIO instance
    image.file.seek(0)
    pil_image = Image.open(image.file)

    # Rewrite the image contents in the memory
    # (bails out with exception on bad data)
    buf = StringIO()
    pil_image.thumbnail((2048, 2048), Image.ANTIALIAS)
    pil_image.save(buf, doc_type)
    image.file = buf

    # Make sure the image has valid extension (can't upload .htm image)
    extension = str(doc_type.lower())
    if not image.name.endswith(u".%s" % extension):
        image.name = image.name + u"." + extension


def convert_to_btc(amount, currency):
    converter = get_rate_converter()
    return converter.convert(currency, "BTC", Decimal(amount))


def get_session_id(request):
    return request.session._session_key


def merge_dicts(dictionary1, dictionary2):
    """ Courtesy of http://stackoverflow.com/a/18424201/315168 """
    output = {}
    for item, value in dictionary1.items():
        if dictionary2.has_key(item):
            if isinstance(dictionary2[item], dict):
                output[item] = merge_dicts(value, dictionary2.pop(item))
        else:
            output[item] = value
    for item, value in dictionary2.items():
         output[item] = value
    return output
