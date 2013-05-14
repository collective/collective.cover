# -*- coding:utf-8 -*-

from collective.cover.config import PROJECTNAME
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

import logging


def rename_content_chooser_resources(context, logger=None):
    """Handler for upgrade step from 2 to 3; renames the 'screenlets'
    resources to 'contentchooser'.
    See: https://github.com/collective/collective.cover/issues/165
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    # first we take care of the CSS registry
    css_tool = getToolByName(context, 'portal_css')
    old_id = '++resource++collective.cover/screenlets.css'
    new_id = '++resource++collective.cover/contentchooser.css'
    if old_id in css_tool.getResourceIds():
        css_tool.renameResource(old_id, new_id)
        logger.info("'%s' resource was renamed to '%s'" % (old_id, new_id))
        css_tool.cookResources()
        logger.info("CSS resources were cooked")
    else:
        logger.debug("'%s' resource not found in portal_css" % old_id)

    # now we mess with the JS registry
    js_tool = getToolByName(context, 'portal_javascripts')
    old_id = '++resource++collective.cover/screenlets.js'
    new_id = '++resource++collective.cover/contentchooser.js'
    if old_id in js_tool.getResourceIds():
        js_tool.renameResource(old_id, new_id)
        logger.info("'%s' resource was renamed to '%s'" % (old_id, new_id))
        js_tool.cookResources()
        logger.info("JS resources were cooked")
    else:
        logger.debug("'%s' resource not found in portal_javascripts" % old_id)


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


def register_styles_record(context, logger=None):
    """Handler for upgrade step from 3 to 4; adds the 'styles' record
    to the registry.
    See: https://github.com/collective/collective.cover/issues/190
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    registry = getUtility(IRegistry)
    record = 'collective.cover.controlpanel.ICoverSettings.styles'

    if record not in registry.records:
        profile = 'profile-collective.cover:upgrade_3_to_4'
        setup = getToolByName(context, 'portal_setup')
        setup.runAllImportStepsFromProfile(profile)
        logger.info("'styles' record added to the registry")
    else:
        logger.debug("'styles' record already in the registry")
