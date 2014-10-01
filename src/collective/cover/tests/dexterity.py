from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema


class ITestContent(model.Schema):
    """A schema for testing dexterity types
    """

    title = schema.TextLine(
        title=u'Title',
    )

    image = NamedBlobImage(
        title=u'Image',
        required=False,
    )
