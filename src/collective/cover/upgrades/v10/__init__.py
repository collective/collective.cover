# -*- coding: utf-8 -*-
from collective.cover.config import PROJECTNAME
from plone import api

import logging

logger = logging.getLogger(PROJECTNAME)


def install_cycle2(context):
    """Install collective.js.cycle2."""
    qi = api.portal.get_tool('portal_quickinstaller')
    qi.installProducts(['collective.js.cycle2'])
    logger.info('collective.js.cycle2 package was installed')
