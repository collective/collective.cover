# -*- coding: utf-8 -*-
from collective.cover.interfaces import ICover
from collective.cover.logger import logger
from persistent.dict import PersistentDict
from plone.namedfile.interfaces import INamedImage
from plone.tiles.interfaces import ITileDataManager


def fix_image_field_modification_time(context):
    """Fix image modification time to be float timestamp instead of string."""

    covers = context.portal_catalog(object_provides=ICover.__identifier__)
    logger.info('About to update {0} objects'.format(len(covers)))
    for cover in covers:
        obj = cover.getObject()
        for tile_id in obj.list_tiles():
            tile = obj.get_tile(tile_id)
            dmgr = ITileDataManager(tile)
            data = dmgr.get()
            for k, v in data.items():
                if not INamedImage.providedBy(v):
                    continue

                mtime_key = '{0}_mtime'.format(k)
                data[mtime_key] = float(data[mtime_key])
                # need to set changes directly into annotation
                dmgr.annotations[dmgr.key] = PersistentDict(data)
                msg = 'Tile {0} at {1} updated'
                logger.info(msg.format(tile_id, cover.getPath()))

    logger.info('Done')
