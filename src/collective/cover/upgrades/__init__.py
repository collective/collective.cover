# -*- coding: utf-8 -*-
from collective.cover.controlpanel import ICoverSettings
from collective.cover.logger import logger
from collective.cover.tiles.list import IListTile
from plone import api
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


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


def cook_css_resources(context):  # pragma: no cover
    """Cook CSS resources."""
    css_tool = api.portal.get_tool('portal_css')
    css_tool.cookResources()
    logger.info('CSS resources were cooked')


def cook_javascript_resources(context):  # pragma: no cover
    """Cook JavaScript resources."""
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.cookResources()
    logger.info('JavaScript resources were cooked')


def change_configlet_permissions(context):
    """Allow Site Administrator to access configlet."""
    cptool = api.portal.get_tool('portal_controlpanel')
    configlet = cptool.getActionObject('Products/cover')
    configlet.permissions = ('collective.cover: Setup',)
    logger.info('configlet permissions updated')


def _get_tiles_inherit_from_list(context):
    """Return a list of all tiles inheriting from the list tile."""
    name = 'collective.cover.EnabledTiles'
    enabled_tiles = getUtility(IVocabularyFactory, name)(context)
    tiles_to_update = []
    for i in enabled_tiles:
        tile = getUtility(ITileType, i.value)
        if issubclass(tile.schema, IListTile):
            tiles_to_update.append(i.value)
    return tiles_to_update


def upgrade_carousel_tiles_custom_url(context):
    """Update structure of tiles inheriting from the list tile."""
    # Get covers
    covers = context.portal_catalog(portal_type='collective.cover.content')
    logger.info('About to update {0} objects'.format(len(covers)))
    tiles_to_update = _get_tiles_inherit_from_list(context)
    msg = '{0} tile types will be updated ({1})'
    logger.info(msg.format(len(tiles_to_update), ', '.join(tiles_to_update)))
    for cover in covers:
        obj = cover.getObject()
        tile_ids = obj.list_tiles(types=tiles_to_update)
        for tile_id in tile_ids:
            tile = obj.get_tile(tile_id)
            old_data = ITileDataManager(tile).get()
            uuids = old_data['uuids']
            if isinstance(uuids, dict):
                # This tile is fixed, carry on
                msg = 'Tile {0} at {1} was already updated'
                logger.info(msg.format(tile_id, cover.getPath()))
                continue
            if not uuids:
                # This tile did not have data, so ignore
                msg = 'Tile {0} at {1} did not have any data'
                logger.info(msg.format(tile_id, cover.getPath()))
                continue

            new_data = dict()
            order = 0
            for uuid in uuids:
                if uuid not in new_data.keys():
                    entry = dict()
                    entry[u'order'] = unicode(order)
                    new_data[uuid] = entry
                    order += 1

            old_data['uuids'] = new_data
            ITileDataManager(tile).set(old_data)
            logger.info('Tile {0} at {1} updated'.format(tile_id, cover.getPath()))

    logger.info('Done')
