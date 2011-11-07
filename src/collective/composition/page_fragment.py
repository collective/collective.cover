from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from collective.composition.composition import ICompositionFragment

from collective.composition import MessageFactory as _


class IPageFragment(form.Schema):
    """
    Building block for composable page
    """
    
    form.model("models/page_fragment.xml")


class PageFragment(dexterity.Item):
    grok.implements(IPageFragment, ICompositionFragment)
    
    def render(self):
        if not self.url:
            return '<p>Please add an URL</p>'
        return self.url
