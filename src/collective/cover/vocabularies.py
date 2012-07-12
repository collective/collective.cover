# -*- coding: utf-8 -*-

from five import grok

from zope.component import getUtility

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

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
