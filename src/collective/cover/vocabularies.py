# -*- coding: utf-8 -*-

from collective.cover.controlpanel import ICoverSettings
from collective.cover.tiles.base import IPersistentCoverTile
from five import grok
from plone.app.vocabularies.types import ReallyUserFriendlyTypesVocabulary
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileType
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class AvailableLayoutsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)

        items = [SimpleTerm(value=i, title=i) for i in sorted(settings.layouts)]
        return SimpleVocabulary(items)

grok.global_utility(AvailableLayoutsVocabulary,
                    name=u'collective.cover.AvailableLayouts')


class AvailableTilesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):

        registry = getUtility(IRegistry)
        tiles = registry[
            'collective.cover.controlpanel.ICoverSettings.available_tiles'
        ]

        items = [SimpleTerm(value=i, title=i) for i in tiles]
        return SimpleVocabulary(items)

grok.global_utility(AvailableTilesVocabulary,
                    name=u'collective.cover.AvailableTiles')


class EnabledTilesVocabulary(object):
    """Return a list of tiles ready to work with collective.cover.
    """
    grok.implements(IVocabularyFactory)

    def _enabled(self, name):
        tile_type = queryUtility(ITileType, name)
        if tile_type:
            return issubclass(tile_type.schema, IPersistentCoverTile)

    def __call__(self, context):
        registry = getUtility(IRegistry)
        tiles = registry['plone.app.tiles']

        tiles = filter(self._enabled, tiles)  # only enabled tiles
        items = []
        for tile in tiles:
            tile_type = getUtility(ITileType, tile)
            items.append(SimpleTerm(value=tile, title=tile_type.title))
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


class TileStylesVocabulary(object):
    """Creates a vocabulary with the available styles stored in the registry.
    """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        items = []
        with_default = False
        if settings.styles is not None:
            styles = list(settings.styles)
            for style in styles:
                if style.count('|') == 1:  # skip in case of formating issues
                    title, css_class = style.split('|')
                    # remove any leading/trailing whitespaces
                    title, css_class = title.strip(), css_class.strip()

                    # make sure that default style is always first
                    if css_class == u'tile-default':
                        items.insert(0, SimpleTerm(value=css_class, title=title))
                        with_default = True
                    else:
                        items.append(SimpleTerm(value=css_class, title=title))

        # force default style if it was removed from configuration
        if not with_default:
            items.insert(0, SimpleTerm(value=u'tile-default', title='-Default-'))

        return SimpleVocabulary(items)

grok.global_utility(TileStylesVocabulary, name=u'collective.cover.TileStyles')
