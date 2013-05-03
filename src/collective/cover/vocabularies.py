# -*- coding: utf-8 -*-

from collective.cover.controlpanel import ICoverSettings
from collective.cover.tiles.base import IPersistentCoverTile
from five import grok
from plone.app.vocabularies.types import ReallyUserFriendlyTypesVocabulary
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


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
        tiles = registry['collective.cover.controlpanel.ICoverSettings.available_tiles']

        items = [SimpleTerm(value=i, title=i) for i in tiles]
        return SimpleVocabulary(items)

grok.global_utility(AvailableTilesVocabulary,
                    name=u'collective.cover.AvailableTiles')


class EnabledTilesVocabulary(object):
    """Return a list of tiles ready to work with collective.cover.
    """
    grok.implements(IVocabularyFactory)

    def _enabled(self, name):
        tile = getMultiAdapter((self.context, self.request), name=name)
        return IPersistentCoverTile.providedBy(tile)

    def __call__(self, context):
        self.context = context
        self.request = getRequest()  # context may be an adapter

        registry = getUtility(IRegistry)
        tiles = registry['plone.app.tiles']

        tiles = filter(self._enabled, tiles)  # only enabled tiles
        items = [SimpleTerm(value=i, title=i) for i in tiles]
        return SimpleVocabulary(items)

grok.global_utility(EnabledTilesVocabulary,
                    name=u'collective.cover.EnabledTiles')


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
