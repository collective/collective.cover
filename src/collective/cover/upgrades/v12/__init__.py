# -*- coding: utf-8 -*-
from collective.cover.config import PROJECTNAME
from collective.cover.logger import logger


def update_role_map(setup_tool):
    """Adds new permission to embed code in the Embed tile."""
    profile = 'profile-{0}:default'.format(PROJECTNAME)
    setup_tool.runImportStepFromProfile(profile, 'rolemap')
    logger.info('Role map updated.')
