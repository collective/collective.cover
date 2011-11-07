from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from collective.composition.composition import ICompositionFragment

from collective.composition import MessageFactory as _


class IContentFragment(form.Schema):
    """
    Content view fragment for composable page
    """
    
    form.model("models/content_fragment.xml")

    relation_field = RelationChoice(title=_(u'My Related Page'),
      source=ObjPathSourceBinder(portal_type='Document'),
      default=None,
      required=False
    )


class ContentFragment(dexterity.Item):
    grok.implements(IContentFragment, ICompositionFragment)

    def render(self):
        content = self.relation_field
        if content is not None:
            content = content.to_object
        else:
            return '<p>Please select a content item</p>'
        method = getattr(content, str(self.method), None)
        if method is not None:
            return method()
        else:
            text = getattr(content, 'getText', None)
            if text:
                return content.getText().decode('UTF-8')
            else:
                return content.Description()
