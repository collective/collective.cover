# -*- coding: utf-8 -*-

from collective.cover.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName

import logging


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
