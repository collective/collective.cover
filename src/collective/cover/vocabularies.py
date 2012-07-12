# -*- coding: utf-8 -*-

from five import grok

from zope.component import getUtility

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from plone.registry.interfaces import IRegistry

from collective.composition.controlpanel import ICompositionSettings


class AvailableLayoutsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICompositionSettings)

        items = [SimpleTerm(value=i, title=i) for i in settings.layouts]
        return SimpleVocabulary(items)

grok.global_utility(AvailableLayoutsVocabulary,
                    name=u'collective.composition.AvailableLayouts')


class AvailableTilesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):

        registry = getUtility(IRegistry)
        tiles = registry['plone.app.tiles']

        # TODO: verify the tile implements IPersistentCompositionTile
        items = [SimpleTerm(value=i, title=i) for i in tiles]
        return SimpleVocabulary(items)

grok.global_utility(AvailableTilesVocabulary,
                    name=u'collective.composition.AvailableTiles')
