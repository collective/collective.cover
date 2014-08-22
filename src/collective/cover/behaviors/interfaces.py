# coding: utf-8
from collective.cover import _
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope.interface import alsoProvides


class IBackgroundImage(model.Schema):

    """Adds the possibility of having a background image on the item."""

    background_image = NamedBlobImage(
        title=_(u'Background image'),
        description=_(
            u'Sets the background image to be used on the item. '
            u'For accessibility reasons, you should not use background images as the sole method of conveying important information.',
        ),
        required=False,
    )

alsoProvides(IBackgroundImage, form.IFormFieldProvider)
