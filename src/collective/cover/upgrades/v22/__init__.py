# -*- coding: utf-8 -*-
"""Upgrade step to populate the new remote_url field on Basic tiles and
known tiles that inherit from it.

We must solve this here for "collective.nitf" tile as we are currently
maintaining 2 branches of collective.cover and there is no easy way to
ensure in collective.nitf code that we are using either
collective.cover >=1.8b1 or >=2.1b1.
"""
from collective.cover import utils
from collective.cover.logger import logger
from collective.cover.upgrades import get_valid_objects
from plone import api
from plone.tiles.interfaces import ITileDataManager


TILE_TYPES = [
    'collective.cover.basic',
    'collective.nitf',
]


def add_remote_url_field(setup_tool):
    """Add remote_url field to Basic tiles."""
    results = get_valid_objects()
    for cover in results:
        for tile_id in cover.list_tiles(TILE_TYPES):
            tile = cover.get_tile(tile_id)
            logger.info('Processing ' + cover.absolute_url_path())
            data_mgr = ITileDataManager(tile)
            data = data_mgr.get()
            if data.get('remote_url'):
                continue  # the field is already populated

            # find the object referenced in the tile
            uuid = data.get('uuid') or ''
            obj = api.content.get(UID=uuid)
            if obj is None:
                continue  # the UUID reference is invalid

            remote_url = utils.get_absolute_url(obj)
            data.update(remote_url=remote_url)
            data_mgr.set(data)
            msg = 'remote_url on "{0}" tile set to: {1}'
            logger.info(msg.format(tile.id, remote_url))
