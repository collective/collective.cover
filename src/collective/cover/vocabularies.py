# -*- coding: utf-8 -*-

from collective.cover.controlpanel import ICoverSettings
from collective.cover.interfaces import IGridSystem
from collective.cover.tiles.base import IPersistentCoverTile
from five import grok
from plone.app.vocabularies.types import ReallyUserFriendlyTypesVocabulary
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileType
from zope.component import getUtility
from zope.component import getUtilitiesFor
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


class GridSystemsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(value=name, title=grid.title)
                 for (name, grid) in getUtilitiesFor(IGridSystem)]
        return SimpleVocabulary(items)

grok.global_utility(GridSystemsVocabulary,
                    name=u'collective.cover.GridSystems')


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


class StylesVocabulary(object):
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
                    else:
                        items.append(SimpleTerm(value=css_class, title=title))

        return SimpleVocabulary(items)


class TileStylesVocabulary(object):
    """ A vocabulary from  available styles stored in the registry,
        with Column & Row styles filtered out.
    """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        base_vocab = StylesVocabulary()
        items = [sTerm for sTerm in base_vocab(context)
                       if not (sTerm.value.startswith('column-') or
                               sTerm.value.startswith('row-')) ]
        default_item = [sTerm for sTerm in items if sTerm.value == u'tile-default']
        if not default_item:
            items.insert(0, SimpleTerm(value=u'tile-default', title='-Default-'))

        return SimpleVocabulary(items)


class RowStylesVocabulary(object):
    """ A vocabulary from  available styles stored in the registry,
        with Column & Tile styles filtered out.
    """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        base_vocab = StylesVocabulary()
        items = [sTerm for sTerm in base_vocab(context)
                       if not (sTerm.value.startswith('column-') or
                               sTerm.value.startswith('tile-')) ]
        default_item = [sTerm for sTerm in items if sTerm.value == u'row-default']
        if not default_item:
            items.insert(0, SimpleTerm(value=u'row-default', title='-Row Default-'))

        return SimpleVocabulary(items)


class ColumnStylesVocabulary(object):
    """ A vocabulary from  available styles stored in the registry,
        with Row & Tile styles filtered out.
    """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        base_vocab = StylesVocabulary()
        items = [sTerm for sTerm in base_vocab(context)
                       if not (sTerm.value.startswith('row-') or
                               sTerm.value.startswith('tile-')) ]
        default_item = [sTerm for sTerm in items if sTerm.value == u'column-default']
        if not default_item:
            items.insert(0, SimpleTerm(value=u'column-default', title='-Column Default-'))

        return SimpleVocabulary(items)


# CSS classes for tiles and for "rows & columns". Separate declarations even
# though they are the same means they can be overridden separately
grok.global_utility(TileStylesVocabulary, name=u'collective.cover.TileStyles')
grok.global_utility(RowStylesVocabulary, name=u'collective.cover.RowStyles')
grok.global_utility(ColumnStylesVocabulary, name=u'collective.cover.ColumnStyles')
