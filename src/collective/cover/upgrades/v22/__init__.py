# -*- coding: utf-8 -*-
from collective.cover.logger import logger
from plone.tiles.interfaces import ITileType
from zope.component import getUtility
from zope.dottedname.resolve import resolve
from zope.schema.interfaces import IVocabularyFactory


def fix_fields(context):
    """tiles here"""

    # Get covers
    covers = context.portal_catalog(portal_type='collective.cover.content')
    iface = 'collective.cover.tiles.collection.ICollectionTile'
    logger.info('About to update {0} objects'.format(len(covers)))
    tiles_to_update = _get_tiles_inherit_from_interface(context, iface=iface)
    logger.info('{0} tile types will be updated ({1})'.format(
        len(tiles_to_update), ', '.join(tiles_to_update)))
    for cover in covers:
        obj = cover.getObject()
        tile_ids = obj.list_tiles(types=tiles_to_update)
        for tile_id in tile_ids:
            tile = obj.get_tile(tile_id)
            tile_conf = tile.get_tile_configuration()

            if 'number_to_show' in tile_conf.keys():
                tile_conf['count'] = tile_conf['number_to_show']
                tile_conf.pop('number_to_show')
                tile.set_tile_configuration(tile_conf)

                msg = 'Tile {0} at {1} updated'
                logger.info(msg.format(tile_id, cover.getPath()))

    logger.info('Done')


def _get_tiles_inherit_from_interface(context, iface=None):
    """Returns a list of all tiles inherited from a given interface."""
    name = 'collective.cover.EnabledTiles'
    tiles_to_update = []
    if iface:
        Iface = resolve(iface)
        enabled_tiles = getUtility(IVocabularyFactory, name)(context)
        tiles_to_update = []
        for i in enabled_tiles:
            tile = getUtility(ITileType, i.value)
            if issubclass(tile.schema, Iface):
                tiles_to_update.append(i.value)
    return tiles_to_update
