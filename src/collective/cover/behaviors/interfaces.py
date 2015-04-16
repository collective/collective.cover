# coding: utf-8
from collective.cover import _
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Invalid


class IRefresh(model.Schema):

    """Reload the current page after a certain amount of time."""

    model.fieldset('settings', fields=['enable_refresh', 'ttl'])

    enable_refresh = schema.Bool(
        title=_(u'Enable refresh'),
        description=_(u'Enable refresh of the current page.'),
        default=False,
    )

    ttl = schema.Int(
        title=_(u'Time to live'),
        description=_(u'Number of seconds after which to reload the current page.',),
        default=300,
    )

alsoProvides(IRefresh, form.IFormFieldProvider)


@form.validator(field=IRefresh['ttl'])
def validate_ttl(value):
    if value <= 0:
        raise Invalid(_(u'Value must be greater than zero.'))


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
