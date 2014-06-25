# -*- coding: utf-8 -*-

from collective.cover.config import PROJECTNAME
from collective.cover.controlpanel import ICoverSettings
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import logging

logger = logging.getLogger(PROJECTNAME)
PROFILE_ID = 'profile-collective.cover:default'


def issue_201(context):
    """Depend on collective.js.bootstrap
    See: https://github.com/collective/collective.cover/issues/201
    """

    # first we take care of the CSS registry
    css_tool = api.portal.get_tool('portal_css')
    old_id = '++resource++collective.cover/bootstrap.min.css'
    if old_id in css_tool.getResourceIds():
        css_tool.unregisterResource(old_id)
        logger.info('"{0}"" resource was removed'.format(old_id))
        css_tool.cookResources()
        logger.info('CSS resources were cooked')
    else:
        logger.debug('"{0}" resource not found in portal_css'.format(old_id))

    # now we mess with the JS registry
    js_tool = api.portal.get_tool('portal_javascripts')
    old_id = '++resource++collective.cover/bootstrap.min.js'
    new_id = '++resource++collective.js.bootstrap/js/bootstrap.min.js'
    if old_id in js_tool.getResourceIds():
        if new_id in js_tool.getResourceIds():
            js_tool.unregisterResource(old_id)
            logger.info('"{0}" resource was removed"'.format(old_id))
        else:
            js_tool.renameResource(old_id, new_id)
            logger.info('"{0}" resource was renamed to "{1}"'.format(old_id, new_id))

        js_tool.cookResources()
        logger.info('JS resources were cooked')
    else:
        logger.debug('"{0}" resource not found in portal_javascripts'.format(old_id))


def issue_303(context):
    """Remove unused bundles from portal_javascripts
    See: https://github.com/collective/collective.cover/issues/303
    """
    FIX_JS_IDS = ['++resource++plone.app.jquerytools.js',
                  '++resource++plone.app.jquerytools.form.js',
                  '++resource++plone.app.jquerytools.overlayhelpers.js',
                  '++resource++plone.app.jquerytools.plugins.js',
                  '++resource++plone.app.jquerytools.dateinput.js',
                  '++resource++plone.app.jquerytools.rangeinput.js',
                  '++resource++plone.app.jquerytools.validator.js',
                  'tiny_mce.js',
                  'tiny_mce_init.js']

    js_tool = api.portal.get_tool('portal_javascripts')
    for id in js_tool.getResourceIds():
        if id in FIX_JS_IDS:
            js = js_tool.getResource(id)
            js.setBundle('default')


def issue_330(context):
    """Add grid_system field to ICoverSettings registry.
    See: https://github.com/collective/collective.cover/issues/330
    and: https://github.com/collective/collective.cover/issues/205
    """
    # Reregister the interface.
    registry = getUtility(IRegistry)
    registry.registerInterface(ICoverSettings)


def layout_edit_permission(context):
    """New permission for Layout edit tab.

    We need to apply our rolemap and typeinfo for this.  Actually,
    instead of applying the complete typeinfo we can explicitly change
    only the permission.
    """
    context.runImportStepFromProfile(PROFILE_ID, 'rolemap')
    types = api.portal.get_tool('portal_types')
    cover_type = types.get('collective.cover.content')
    if cover_type is None:
        # Can probably not happen, but let's be gentle.
        context.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
        return
    action = cover_type.getActionObject('object/layoutedit')
    action.permissions = (u'collective.cover: Can Edit Layout', )


def cook_css_resources(context):
    """Cook css resources.
    """
    css_tool = api.portal.get_tool('portal_css')
    css_tool.cookResources()
    logger.info('CSS resources were cooked')


def cook_javascript_resources(context):
    """Cook javascript resources.
    """
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.cookResources()
    logger.info('Javascript resources were cooked')


def change_configlet_permissions(context):
    """Allow Site Administrator to access configlet."""
    cptool = api.portal.get_tool('portal_controlpanel')
    configlet = cptool.getActionObject('Products/cover')
    configlet.permissions = ('collective.cover: Setup',)
    logger.info('configlet permissions updated')
