# -*- coding: utf-8 -*-
"""Upgrade step to show the value stored in remote_url field of Basic
tiles and other known tiles that inherit from it.

An upgrade step on profile version 22 had unintended consequences: if
tiles were updated or populated from an alternate URL the link stored
could be invalid. We just show on log any possible issues to help
fixing them by hand.

For more information, see:

https://github.com/collective/collective.cover/issues/839
"""
from collective.cover.logger import logger
from collective.cover.upgrades import get_valid_objects
from plone.tiles.interfaces import ITileDataManager


# XXX: 'collective.nitf' tile inherits from 'collective.cover.basic';
# we included it here as we are currently maintaining 2 branches of
# collective.cover and there is no easy way to ensure we are using
# either collective.cover >=1.8b1 or >=2.1b1 in collective.nitf code
TILE_TYPES = [
    'collective.cover.basic',
    'collective.nitf',
]


def show_remote_url_field(setup_tool):
    """Show remote_url field on Basic tiles."""
    logger.info(__doc__)
    results = get_valid_objects()
    for cover in results:
        for tile_id in cover.list_tiles(TILE_TYPES):
            tile = cover.get_tile(tile_id)
            data_mgr = ITileDataManager(tile)
            data = data_mgr.get()
            remote_url = data.get('remote_url')
            if not remote_url:
                continue

            # show information on possible issue
            path = cover.absolute_url_path()
            msg = '{0} ("{1}"): remote_url={2}'
            logger.info(msg.format(path, tile_id, remote_url))
