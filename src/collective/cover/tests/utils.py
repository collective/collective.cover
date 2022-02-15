# -*- coding: utf-8 -*-
"""Helper functions to create test content."""
from datetime import timedelta
from plone import api
from plone.app.event.base import localized_now
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage

import six


def create_standard_content_for_tests(portal):
    """Create one instance of each standard content type, at least."""
    with api.env.adopt_roles(["Manager"]):
        api.content.create(
            container=portal,
            type="Collection",
            title=u"Mandelbrot set",
            description=u"Image gallery of a zoom sequence",
            query=[
                {
                    "i": "portal_type",
                    "o": "plone.app.querystring.operation.selection.any",
                    "v": ["Image"],
                }
            ],
        )

        obj = api.content.create(
            container=portal,
            type="Document",
            title=u"My document",
            description=u"This document was created for testing purposes",
        )

        set_text_field(obj, u"<p>The quick brown fox jumps over the lazy dog</p>")
        now = localized_now()
        tomorrow = now + timedelta(days=1)

        api.content.create(
            container=portal,
            type="Event",
            title=u"My event",
            start=now,
            end=tomorrow,
        )

        api.content.create(
            container=portal,
            type="File",
            title=u"My file",
            description=u"This file was created for testing purposes",
        )

        api.content.create(
            container=portal,
            type="Folder",
            title=u"My folder",
            description=u"This folder was created for testing purposes",
        )

        api.content.create(
            container=portal,
            type="Link",
            id="my-link",
            title=u"Test link",
            description=u"This link was created for testing purposes",
            remoteUrl=u"http://plone.org",
        )

        api.content.create(
            container=portal,
            type="News Item",
            id="my-news-item",
            title=u"Test news item",
            description=u"This news item was created for testing purposes",
        )


def set_image_field(obj, image):
    """Set image field in object."""
    data = image if isinstance(image, six.binary_type) else image.getvalue()
    obj.image = NamedBlobImage(data=data, contentType="image/jpeg")
    obj.reindexObject()


def set_file_field(obj, _file):
    """Set file field in object."""
    obj.file = NamedBlobFile(data=_file, contentType="text/plain")
    obj.reindexObject()


def set_text_field(obj, text):
    """Set text field in object."""
    obj.text = RichTextValue(text, "text/html", "text/html")
    obj.reindexObject()
