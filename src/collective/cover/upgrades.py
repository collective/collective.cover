# -*- coding:utf-8 -*-

from collective.cover import _
from collective.cover.config import DEFAULT_AVAILABLE_TILES
from collective.cover.config import PROJECTNAME
from plone.registry import field
from plone.registry import Record
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import logging


def register_available_tiles_record(context, logger=None):
    """Handler for upgrade step from 2 to 3; adds the 'available_tiles' record
    to the registry.
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    registry = getUtility(IRegistry)
    record = 'collective.cover.controlpanel.ICoverSettings.available_tiles'

    if record not in registry.records:
        available_tiles = field.List(
            title=_(u"Available tiles"),
            description=_(u"This tiles will be available for layout creation."),
            required=True,
            default=DEFAULT_AVAILABLE_TILES,
            value_type=field.Choice(
                vocabulary=u'collective.cover.EnabledTiles'),
        )

        registry.records[record] = Record(available_tiles)
        logger.info("'available_tiles' record was added to the registry")
    else:
        logger.info("'available_tiles' record already exists in the registry")
