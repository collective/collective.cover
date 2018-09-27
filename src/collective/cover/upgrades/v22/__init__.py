# -*- coding: utf-8 -*-
from collective.cover import utils
from collective.cover.upgrades import get_valid_objects
from plone import api
from plone.tiles.interfaces import ITileDataManager


def add_remote_url_field(setup_tool):
    """Add remote_url field to Basic tiles."""
    results = get_valid_objects()
    for cover in results:
        for tile_id in cover.list_tiles('collective.cover.basic'):
            tile = cover.get_tile(tile_id)
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
