from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.app.portlets.interfaces import IPortletManager, IPortletRenderer
from plone.app.portlets.interfaces import IPortletAssignmentMapping

from collective.composition.composition import ICompositionFragment

from collective.composition import MessageFactory as _


class IPortletFragment(form.Schema):
    """
    Content view fragment for composable page
    """
    
    form.model("models/portlet_fragment.xml")


class PortletFragment(dexterity.Item):
    grok.implements(IPortletFragment, ICompositionFragment)

    def render(self):
        if not self.portlet:
            return '<p>Please select a portlet</p>'
        uid, column, name = self.portlet.split(':')
        if uid == '/':
            target_context = self.portal_url.getPortalObject()
        else:
            target_uid = self.uid_catalog(UID=uid)
            if target_uid:
                target_context = target_uid[0].getObject()
            else:
                raise ValueError("Portlet to mirror does not exist")
        manager = getUtility(IPortletManager,
            name=u'plone.%scolumn' % column,
            context=target_context)
        mapping = getMultiAdapter((target_context, manager),
            IPortletAssignmentMapping)
        assignment = mapping[name]
        view = target_context.restrictedTraverse('@@plone')
        request = getattr(self, "REQUEST", None)
        if request is None:
            return '<p>Portlet not found</p>'
        renderer = getMultiAdapter((target_context,
                request,
                view,
                manager,
                assignment),
            IPortletRenderer)
        renderer = renderer.__of__(target_context)
        return renderer.render()
