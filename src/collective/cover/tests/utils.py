# -*- coding: utf-8 -*-
"""Helper functions to create test content and work around API
inconsistencies among Archetypes and Dexterity.
"""
from datetime import datetime
from datetime import timedelta
from tzlocal import get_localzone


today = datetime.today()
tomorrow = today + timedelta(days=1)

TZNAME = get_localzone().zone


def create_standard_content_for_tests(portal):
    """Create one instance of each standard content type, at least."""
    from DateTime import DateTime
    from plone import api

    with api.env.adopt_roles(['Manager']):
        api.content.create(
            container=portal,
            type='Collection',
            title=u'Mandelbrot set',
            description=u'Image gallery of a zoom sequence',
            query=[{
                'i': 'Type',
                'o': 'plone.app.querystring.operation.string.is',
                'v': ['Image'],
            }]
        )

        obj = api.content.create(
            container=portal,
            type='Document',
            title=u'My document',
            description=u'This document was created for testing purposes',
        )

        # XXX: handle setting text field for both, Archetypes and Dexterity
        set_text_field(obj, u'<p>The quick brown fox jumps over the lazy dog</p>')

        api.content.create(
            container=portal,
            type='Event',
            title=u'My event',
            startDate=DateTime(today),  # Archetypes
            endDate=DateTime(tomorrow),
            start=today,  # Dexterity
            end=tomorrow,
            timezone=TZNAME,
        )

        api.content.create(
            container=portal,
            type='File',
            title=u'My file',
            description=u'This file was created for testing purposes',
        )

        api.content.create(
            container=portal,
            type='Folder',
            title=u'My folder',
            description=u'This folder was created for testing purposes',
        )

        api.content.create(
            container=portal,
            type='Link',
            id='my-link',
            title=u'Test link',
            description=u'This link was created for testing purposes',
            remoteUrl=u'http://plone.org',
        )

        api.content.create(
            container=portal,
            type='News Item',
            id='my-news-item',
            title=u'Test news item',
            description=u'This news item was created for testing purposes',
        )


def set_image_field(obj, image):
    """Set image field in object on both, Archetypes and Dexterity."""
    from plone.namedfile.file import NamedBlobImage
    try:
        obj.setImage(image)  # Archetypes
    except AttributeError:
        # Dexterity
        data = image if type(image) == str else image.getvalue()
        obj.image = NamedBlobImage(data=data, contentType='image/jpeg')
    finally:
        obj.reindexObject()


def set_file_field(obj, file):
    """Set file field in object on both, Archetypes and Dexterity."""
    from plone.namedfile.file import NamedBlobFile
    try:
        obj.setFile(file)  # Archetypes
    except AttributeError:
        # Dexterity
        obj.file = NamedBlobFile(data=file, contentType='text/plain')
    finally:
        obj.reindexObject()


def set_text_field(obj, text):
    """Set text field in object on both, Archetypes and Dexterity."""
    from plone.app.textfield.value import RichTextValue
    try:
        obj.setText(text)  # Archetypes
    except AttributeError:
        obj.text = RichTextValue(text, 'text/html', 'text/html')  # Dexterity
    finally:
        obj.reindexObject()
