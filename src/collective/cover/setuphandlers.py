# -*- coding:utf-8 -*-
'''
Created on 01/04/2013

@author: jpg
'''
import logging
from collective.cover.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName


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
