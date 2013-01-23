# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


PROFILE_ID = 'profile-collective.cover:default'


def inline_edition_control_panel_update(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')
    context.runImportStepFromProfile(PROFILE_ID, 'jsregistry')
