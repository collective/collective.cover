# -*- coding: utf-8 -*-
from collective.cover.logger import logger
from persistent.dict import PersistentDict
from plone.namedfile.interfaces import INamedImage
from plone.tiles.interfaces import ITileDataManager


def fix_image_modified_date(context):
    """Update all tiles to fix modified date"""

    covers = context.portal_catalog(portal_type='collective.cover.content')
    logger.info('About to update {0} objects'.format(len(covers)))
    for cover in covers:
        obj = cover.getObject()
        for tile_id in obj.list_tiles():
            tile = obj.get_tile(tile_id)
            dmgr = ITileDataManager(tile)
            data = dmgr.get()
            for k, v in data.items():
                if INamedImage.providedBy(v):
                    mtime_key = '{0}_mtime'.format(k)
                    data[mtime_key] = float(data[mtime_key])
            # need to set changes directly into annotation
            dmgr.annotations[dmgr.key] = PersistentDict(data)
            msg = 'Tile {0} at {1} updated'
            logger.info(msg.format(tile_id, cover.getPath()))

    logger.info('Done')
