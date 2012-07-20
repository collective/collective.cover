# -*- coding: utf-8 -*-

from Acquisition import aq_get

from zope.component import getUtility

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.site.hooks import getSite
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName

from five import grok
from plone.registry.interfaces import IRegistry

from collective.cover.controlpanel import ICoverSettings


class AvailableLayoutsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)

        items = [SimpleTerm(value=i, title=i) for i in settings.layouts]
        return SimpleVocabulary(items)

grok.global_utility(AvailableLayoutsVocabulary,
                    name=u'collective.cover.AvailableLayouts')


class AvailableTilesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):

        registry = getUtility(IRegistry)
        tiles = registry['plone.app.tiles']

        # TODO: verify the tile implements IPersistentCoverTile
        items = [SimpleTerm(value=i, title=i) for i in tiles]
        return SimpleVocabulary(items)

grok.global_utility(AvailableTilesVocabulary,
                    name=u'collective.cover.AvailableTiles')


class AvailableContentTypesVocabulary(object):
    """ Customized version of plone.app.vocabularies.UserFriendlyTypes; we
    don't want covers to be listed.
    """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        site = getSite()
        ptool = getToolByName(site, 'plone_utils', None)
        ttool = getToolByName(site, 'portal_types', None)
        if ptool is None or ttool is None:
            return SimpleVocabulary([])

        request = aq_get(ttool, 'REQUEST', None)
        items = [(translate(ttool[t].Title(), context=request), t)
                 for t in ptool.getUserFriendlyTypes()]
        items.sort()
        items = [SimpleTerm(i[1], i[1], i[0]) for i in items
                 if i[1] != u'collective.cover.content']
        return SimpleVocabulary(items)


grok.global_utility(AvailableContentTypesVocabulary,
                    name=u'collective.cover.AvailableContentTypes')
