# -*- coding: utf-8 -*-

from five import grok

from zope.interface import implements
from zope.component import getUtility
from zope.component import getMultiAdapter

from zope.component.interfaces import IFactory

from zope.app.container.interfaces import IAdding

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from plone.app.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IPortletAssignmentMapping

from plone.portlets.interfaces import ILocalPortletAssignable

from plone.registry.interfaces import IRegistry

from collective.composition.controlpanel import ICompositionSettings
from collective.composition import _


class ContextPortlets(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'collective.composition.vocabularies.portlets')

    def __call__(self, context):
        assignables = context.portal_catalog(object_provides=ILocalPortletAssignable.__identifier__)
        results = self.getPortletAssignments(context.portal_url.getPortalObject())
        for assignable in assignables:
            items = self.getPortletAssignments(assignable.getObject())
            results += items
        results.sort()
        return SimpleVocabulary([result[1] for result in results])

    def getPortletAssignments(self, target):
        items = []
        if hasattr(target, 'UID'):
            uid = target.UID()
        else:
            uid = '/'
        path = target.absolute_url_path()
        left_column = getUtility(IPortletManager,
                                 name=u'plone.leftcolumn',
                                 context=target)
        right_column = getUtility(IPortletManager,
                                  name=u'plone.rightcolumn',
                                  context=target)
        left_manager = getMultiAdapter((target, left_column),
                                       IPortletAssignmentMapping)
        right_manager = getMultiAdapter((target, right_column),
                                        IPortletAssignmentMapping)
        for assignment in left_manager.values():
            name = '%s:left:%s' % (uid, assignment.id)
            title = '%s - %s' % (path, assignment.title)
            simpleterm = SimpleTerm(name, name, title)
            items.append((path, simpleterm))
        for assignment in right_manager.values():
            name = '%s:right:%s' % (uid, assignment.id)
            title = '%s - %s' % (path, assignment.title)
            simpleterm = SimpleTerm(name, name, title)
            items.append((path, simpleterm))
        return items


class LayoutVocabulary(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'collective.composition.vocabularies.layouts')

    def __call__(self, context):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICompositionSettings)

        items = [SimpleTerm(value=i, title=i) for i in settings.layouts]
        return SimpleVocabulary(items)
