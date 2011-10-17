from five import grok
from plone.directives import dexterity, form

from zope.component import getAdapter

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from collective.composition.layout import ICompositionLayout

from collective.composition import MessageFactory as _


class IComposition(form.Schema):
    """
    Composable page
    """
    form.model("models/composition.xml")


class Composition(dexterity.Container):
    grok.implements(IComposition)
    
    def render(self):
        layout_name = self.composition_layout
        layout = getAdapter((self,), ICompositionLayout, name=layout_name)
        return layout.render()

class View(grok.View):
    grok.context(IComposition)
    grok.require('zope2.View')
    grok.name('view')
    

class Compose(grok.View):
    grok.context(IComposition)
    grok.require('zope2.View')
    
