# -*- coding: utf-8 -*-
from collective.cover.controlpanel import ICoverSettings
from collective.cover.logger import logger
from plone import api


def register_calendar_tile(setup_tool):
    """Register calendar tile and make it available for inmediate use."""
    tile = u'collective.cover.calendar'

    record = dict(name='plone.app.tiles')
    registered_tiles = api.portal.get_registry_record(**record)
    if tile not in registered_tiles:
        registered_tiles.append(tile)
        api.portal.set_registry_record(value=registered_tiles, **record)

    record = dict(interface=ICoverSettings, name='available_tiles')
    available_tiles = api.portal.get_registry_record(**record)
    if tile not in available_tiles:
        available_tiles.append(tile)
        api.portal.set_registry_record(value=available_tiles, **record)

    logger.info('Calendar tile registered and made available')


def register_calendar_script(setup_tool):
    """Register script to deal with tile's next/prev events."""
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.registerResource('++resource++collective.cover/js/main.js')
    logger.info('Calendar script registered')
