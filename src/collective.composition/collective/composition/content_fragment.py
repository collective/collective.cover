from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from collective.composition.page_fragment import PageFragment

from collective.composition import MessageFactory as _


class IContentFragment(form.Schema):
    """
    Content view fragment for composable page
    """
    
    form.model("models/content_fragment.xml")


class ContentFragment(PageFragment):
    grok.implements(IContentFragment)

