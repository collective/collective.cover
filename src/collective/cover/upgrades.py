# -*- coding: utf-8 -*-

from collective.cover.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName

import logging


def issue_201(context, logger=None):
    """Depend on collective.js.bootstrap
    See: https://github.com/collective/collective.cover/issues/201
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    # first we take care of the CSS registry
    css_tool = getToolByName(context, 'portal_css')
    old_id = '++resource++collective.cover/bootstrap.min.css'
    if old_id in css_tool.getResourceIds():
        css_tool.unregisterResource(old_id)
        logger.info("'{0}' resource was removed".format(old_id))
        css_tool.cookResources()
        logger.info("CSS resources were cooked")
    else:
        logger.debug("'{0}' resource not found in portal_css".format(old_id))

    # now we mess with the JS registry
    js_tool = getToolByName(context, 'portal_javascripts')
    old_id = '++resource++collective.cover/bootstrap.min.js'
    new_id = '++resource++collective.js.bootstrap/js/bootstrap.min.js'
    if old_id in js_tool.getResourceIds():
        js_tool.renameResource(old_id, new_id)
        logger.info("'{0}' resource was renamed to '{1}'".format(old_id, new_id))
        js_tool.cookResources()
        logger.info("JS resources were cooked")
    else:
        logger.debug("'{0}' resource not found in portal_javascripts".format(old_id))
