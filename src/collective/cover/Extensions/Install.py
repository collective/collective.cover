# -*- coding: utf-8 -*-

from collective.cover.config import PROJECTNAME
from plone import api


def uninstall(portal, reinstall=False):
    if not reinstall:
        profile = 'profile-{0}:uninstall'.format(PROJECTNAME)
        setup_tool = api.portal.get_tool('portal_setup')
        setup_tool.runAllImportStepsFromProfile(profile)
        return 'Ran all uninstall steps.'
