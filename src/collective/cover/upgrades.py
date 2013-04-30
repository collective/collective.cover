# -*- coding:utf-8 -*-

from collective.cover.config import PROJECTNAME
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

import logging


def register_available_tiles_record(context, logger=None):
    """Handler for upgrade step from 2 to 3; adds the 'available_tiles' record
    to the registry.
    See: https://github.com/collective/collective.cover/issues/191
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    registry = getUtility(IRegistry)
    record = 'collective.cover.controlpanel.ICoverSettings.available_tiles'

    if record not in registry.records:
        profile = 'profile-collective.cover:upgrade_2_to_3'
        setup = getToolByName(context, 'portal_setup')
        setup.runAllImportStepsFromProfile(profile)
        logger.info("'available_tiles' record added to the registry")
    else:
        logger.debug("'available_tiles' record already in the registry")
