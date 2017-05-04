# -*- coding: utf-8 -*-
from collective.cover.config import IS_PLONE_5
from collective.cover.controlpanel import ICoverSettings
from collective.cover.interfaces import IGridSystem
from collective.cover.tiles.base import IPersistentCoverTile
from plone.app.vocabularies.types import ReallyUserFriendlyTypesVocabulary
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileType
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class AvailableLayoutsVocabulary(object):

    def __call__(self, context):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)

        items = [SimpleTerm(value=i, title=i) for i in sorted(settings.layouts)]
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class AvailableTilesVocabulary(object):

    def __call__(self, context):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        tiles = settings.available_tiles

        # FIXME: https://github.com/collective/collective.cover/issues/633
        if IS_PLONE_5 and 'collective.cover.calendar' in tiles:
            tiles.remove('collective.cover.calendar')

        items = [SimpleTerm(value=i, title=i) for i in tiles]
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class GridSystemsVocabulary(object):

    def __call__(self, context):
        items = [SimpleTerm(value=name, title=grid.title)
                 for (name, grid) in getUtilitiesFor(IGridSystem)]
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class EnabledTilesVocabulary(object):

    """Return a list of tiles ready to work with collective.cover."""

    def _enabled(self, name):
        # FIXME: https://github.com/collective/collective.cover/issues/633
        if IS_PLONE_5 and name == 'collective.cover.calendar':
            return False

        tile_type = queryUtility(ITileType, name)
        if tile_type and tile_type.schema:
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


@implementer(IVocabularyFactory)
class AvailableContentTypesVocabulary(ReallyUserFriendlyTypesVocabulary):
    """
    Inherit from plone.app.vocabularies.ReallyUserFriendlyTypes; and filter
    the results. We don't want covers to be listed.
    """

    def __call__(self, context):
        items = super(AvailableContentTypesVocabulary, self).__call__(context)
        items = [i for i in items if i.token != 'collective.cover.content']
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class TileStylesVocabulary(object):
    """Creates a vocabulary with the available styles stored in the registry.
    """

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
