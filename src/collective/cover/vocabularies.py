# -*- coding: utf-8 -*-

from zope.component import getUtility

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from five import grok
from plone.registry.interfaces import IRegistry

from plone.app.vocabularies.types import ReallyUserFriendlyTypesVocabulary

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


class AvailableContentTypesVocabulary(ReallyUserFriendlyTypesVocabulary):
    """
    Inherit from plone.app.vocabularies.ReallyUserFriendlyTypes; and filter
    the results. We don't want covers to be listed.
    """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        items = super(AvailableContentTypesVocabulary, self).__call__(context)
        items = [i for i in items if i.token != 'collective.cover.content']
        return SimpleVocabulary(items)


grok.global_utility(AvailableContentTypesVocabulary,
                    name=u'collective.cover.AvailableContentTypes')
