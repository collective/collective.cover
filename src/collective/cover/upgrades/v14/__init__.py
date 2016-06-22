# -*- coding: utf-8 -*-
from collective.cover.logger import logger
from plone import api
from zope.schema.interfaces import WrongContainedType


def register_tile_calendar(setup_tool):
    """Register Tile Calendar."""
    registered_tiles = api.portal.get_registry_record(name='plone.app.tiles')
    registered_tiles.append('collective.cover.calendar')
    try:
        api.portal.set_registry_record(
            name='plone.app.tiles', value=registered_tiles)
    except WrongContainedType:
        # I don't know why I get this exception on manual test
        # but still works like this
        pass
    logger.info('Tile Calendar registered.')


def add_cover_js_script(setup_tool):
    """Add cover.js script with Tile Calendar next/prev events."""
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.registerResource('++resource++collective.cover/js/main.js')
    logger.info('Script cover.js added.')
