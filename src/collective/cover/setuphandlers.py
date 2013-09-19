# -*- coding: utf-8 -*-

from collective.cover.config import PROJECTNAME
from collective.cover.upgrades import unicode_lexicon
from Products.CMFCore.utils import getToolByName

import logging
import pkg_resources

PLONE_VERSION = pkg_resources.require("Plone")[0].version


def to_plone43(context, logger=None):
    """
    """
    if logger is None:
        # Called as upgrade step: define our own logger
        logger = logging.getLogger(PROJECTNAME)

    qi = getToolByName(context, 'portal_quickinstaller')
    if 'plone.app.relationfield' not in \
       [i['id'] for i in qi.listInstalledProducts()]:
        qi.installProduct('plone.app.relationfield')


def import_various(context):
    """ Import step for configuration that is not handled in XML files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('collective.cover.marker.txt') is None:
        return

    site = context.getSite()
    if PLONE_VERSION < '4.3':
        # On Plone versions < 4.3 we call this upgrade step
        # to try to install Products.UnicodeLexicon
        unicode_lexicon(site)
