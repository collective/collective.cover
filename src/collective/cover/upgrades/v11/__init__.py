# -*- coding: utf-8 -*-
from collective.cover.controlpanel import ICoverSettings
from collective.cover.interfaces import ICover
from collective.cover.logger import logger
from collective.cover.tiles.configuration import ANNOTATIONS_KEY_PREFIX as PREFIX
from collective.cover.upgrades import _get_tiles_inherit_from_list
from copy import deepcopy
from plone import api
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from zope.component import getUtility

import json


def fix_persistentmap_to_dict(context):
    """Internal structure was reverted from using PersistentMapping.
    Fix tiles here"""

    # Get covers
    covers = context.portal_catalog(portal_type='collective.cover.content')
    logger.info('About to update {0} objects'.format(len(covers)))
    tiles_to_update = _get_tiles_inherit_from_list(context)
    logger.info('{0} tile types will be updated ({1})'.format(
        len(tiles_to_update), ', '.join(tiles_to_update)))
    for cover in covers:
        obj = cover.getObject()
        tile_ids = obj.list_tiles(types=tiles_to_update)
        for tile_id in tile_ids:
            tile = obj.get_tile(tile_id)
            old_data = ITileDataManager(tile).get()
            uuids = old_data['uuids']
            if isinstance(uuids, dict):
                # This tile is fixed, carry on
                msg = 'Tile {0} at {1} was already updated'
                logger.info(msg.format(tile_id, cover.getPath()))
                continue
            if not uuids:
                # This tile did not have data, so ignore
                msg = 'Tile {0} at {1} did not have any data'
                logger.info(msg.format(tile_id, cover.getPath()))
                continue

            new_data = dict()
            for k, v in uuids.items():
                new_data[k] = v

            old_data['uuids'] = new_data
            ITileDataManager(tile).set(old_data)

            msg = 'Tile {0} at {1} updated'
            logger.info(msg.format(tile_id, cover.getPath()))

    logger.info('Done')


def _remove_css_class_layout(layout, is_child=False):
    """Recursivelly remove class attribute from layout."""
    if not is_child:
        layout = json.loads(layout)
    fixed_layout = []
    for row in layout:
        fixed_row = {
            k: v
            for k, v in row.iteritems()
            if k != u'class'
        }
        if u'children' in fixed_row:
            fixed_row[u'children'] = _remove_css_class_layout(fixed_row[u'children'], True)
        fixed_layout.append(fixed_row)
    if is_child:
        return fixed_layout
    else:
        fixed_layout = json.dumps(fixed_layout)
        return fixed_layout.decode('utf-8')


def remove_css_class_layout(context):
    """Remove CSS class from registry and cover layouts."""
    logger.info('CSS classes will be removed from Cover layouts.')
    # Fix registry layouts
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICoverSettings)
    fixed_layouts = {}
    for name, layout in settings.layouts.iteritems():
        fixed_layouts[name] = _remove_css_class_layout(layout)
    settings.layouts = fixed_layouts
    logger.info('Registry layouts were updated.')

    # Fix cover layouts
    covers = context.portal_catalog(object_provides=ICover.__identifier__)
    logger.info('Layout of {0} objects will be updated'.format(len(covers)))

    for cover in covers:
        obj = cover.getObject()
        obj.cover_layout = _remove_css_class_layout(obj.cover_layout)
        logger.info('"{0}" was updated'.format(obj.absolute_url_path()))


def remove_orphan_annotations(context):
    """Remove annotations left behind after tile removal.

    The bug was fixed in bf386fee but no upgrade step was provided to
    clean up the objects.
    """
    catalog = api.portal.get_tool('portal_catalog')
    results = catalog(object_provides=ICover.__identifier__)
    logger.info('Checking {0} objects for orphan annotations'.format(len(results)))

    for brain in results:
        cover = brain.getObject()
        tiles = cover.list_tiles()

        try:
            orphan_annotations = [
                k for k in cover.__annotations__.keys()
                if k.startswith(PREFIX) and k.split('.')[3] not in tiles
            ]

            for k in orphan_annotations:
                del(cover.__annotations__[k])

            if orphan_annotations:
                msg = 'Removed {0} annotations from "{1}"'
                logger.info(
                    msg.format(len(orphan_annotations), cover.absolute_url_path()))

        except AttributeError:
            pass  # cover with no annotations


def _simplify_layout(layout, is_child=False):
    """Recursivelly move column-size to parent and remove data attribute from layout."""
    if not is_child:
        layout = json.loads(layout)
    fixed_layout = []
    for row in layout:
        fixed_row = deepcopy(row)
        if u'data' in row:
            if u'column-size' in row[u'data']:
                fixed_row[u'column-size'] = fixed_row[u'data'][u'column-size']
            del(fixed_row[u'data'])
        if u'children' in fixed_row:
            fixed_row[u'children'] = _simplify_layout(fixed_row[u'children'], True)
        fixed_layout.append(fixed_row)
    if is_child:
        return fixed_layout
    else:
        fixed_layout = json.dumps(fixed_layout)
        return fixed_layout.decode('utf-8')


def simplify_layout(context):
    """Move column-size to parent and remove data attribute from layout."""
    logger.info('Cover layouts will be simplified.')
    # Fix registry layouts
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICoverSettings)
    fixed_layouts = {}
    for name, layout in settings.layouts.iteritems():
        fixed_layouts[name] = _simplify_layout(layout)
    settings.layouts = fixed_layouts
    logger.info('Registry layouts were updated.')

    # Fix cover layouts
    covers = context.portal_catalog(object_provides=ICover.__identifier__)
    logger.info('Layout of {0} objects will be updated'.format(len(covers)))

    for cover in covers:
        obj = cover.getObject()
        obj.cover_layout = _simplify_layout(obj.cover_layout)
        logger.info('"{0}" was updated'.format(obj.absolute_url_path()))
