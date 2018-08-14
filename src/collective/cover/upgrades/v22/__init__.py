# -*- coding: utf-8 -*-
from collective.cover.controlpanel import ICoverSettings
from collective.cover.interfaces import ICover
from collective.cover.logger import logger
from collective.cover.tiles.configuration import ANNOTATIONS_KEY_PREFIX as PREFIX
from collective.cover.upgrades import _get_tiles_inherit_from_interface
from copy import deepcopy
from plone import api
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from six import iteritems
from zope.component import getUtility

import json


def fix_fields(context):
    """tiles here"""

    # Get covers
    covers = context.portal_catalog(portal_type='collective.cover.content')
    iface = "collective.cover.tiles.collection.ICollectionTile"
    logger.info('About to update {0} objects'.format(len(covers)))
    tiles_to_update = _get_tiles_inherit_from_interface(context,
            iface=iface)
    logger.info('{0} tile types will be updated ({1})'.format(
        len(tiles_to_update), ', '.join(tiles_to_update)))
    for cover in covers:
        obj = cover.getObject()
        tile_ids = obj.list_tiles(types=tiles_to_update)
        for tile_id in tile_ids:
            tile = obj.get_tile(tile_id)
            tile_conf = tile.get_tile_configuration()

            if tile_conf.has_key('number_to_show'):
                tile_conf['count'] = tile_conf['number_to_show']
                tile_conf.pop('number_to_show')
                tile.set_tile_configuration(tile_conf)

                msg = 'Tile {0} at {1} updated'
                logger.info(msg.format(tile_id, cover.getPath()))

    logger.info('Done')
