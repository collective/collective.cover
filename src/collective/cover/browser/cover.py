# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from collective.cover.controlpanel import ICoverSettings
from collective.cover.interfaces import ICover
from collective.cover.interfaces import IGridSystem
from collective.cover.tiles.list import ListTile
from five import grok
from plone import api
from plone.dexterity.events import EditBegunEvent
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUIDGenerator
from Products.CMFCore.exceptions import BadRequest
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.event import notify

import json

grok.templatedir('templates')


class View(grok.View):
    grok.context(ICover)
    grok.require('zope2.View')
    grok.name('view')


class Standard(grok.View):
    grok.context(ICover)
    grok.require('zope2.View')
    grok.name('standard')


class AddCTWidget(grok.View):
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        widget_type = self.request.get('widget_type')
        widget_title = self.request.get('widget_title')
        column_id = self.request.get('column_id')
        widget = createContentInContainer(self.context,
                                          widget_type,
                                          title=widget_title,
                                          checkConstraints=False)
        widget_url = widget.absolute_url()
        return json.dumps({'column_id': column_id,
                           'widget_type': widget_type,
                           'widget_title': widget_title,
                           'widget_id': widget.id,
                           'widget_url': widget_url})


class AddTileWidget(grok.View):
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        uuid = getUtility(IUUIDGenerator)
        widget_type = self.request.get('widget_type')
        widget_title = self.request.get('widget_title')
        column_id = self.request.get('column_id')

        id = uuid()
        context_url = self.context.absolute_url()
        widget_url = '{0}/@@{1}/{2}'.format(context_url, widget_type, id)

        # Let's store locally info regarding tiles
        annotations = IAnnotations(self.context)
        current_tiles = annotations.get('current_tiles', {})

        current_tiles[id] = {'type': widget_type,
                             'title': widget_title}
        annotations['current_tiles'] = current_tiles

        return json.dumps({'column_id': column_id,
                           'widget_type': widget_type,
                           'widget_title': widget_title,
                           'widget_id': id,
                           'widget_url': widget_url})


class SetWidgetMap(grok.View):
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        widget_map = self.request.get('widget_map')
        remove = self.request.get('remove', None)
        self.context.set_widget_map(widget_map, remove)
        return json.dumps('success')


class UpdateWidget(grok.View):
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        widget_id = self.request.get('wid')
        if widget_id in self.context:
            return self.context[widget_id].render()
        else:
            return 'Widget does not exist'


class RemoveTileWidget(grok.View):
    # XXX: This should be part of the plone.app.tiles package or similar
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')
    grok.name('removetilewidget')

    def __call__(self):
        template = self.template
        if 'form.submitted' not in self.request:
            return template.render(self)

        annotations = IAnnotations(self.context)
        current_tiles = annotations.get('current_tiles', {})
        tile_id = self.request.get('wid', None)

        if tile_id in current_tiles:
            widget_type = current_tiles[tile_id]['type']
            # Let's remove all traces of the value stored in the tile
            widget_uri = '@@{0}/{1}'.format(widget_type, tile_id)
            tile = self.context.restrictedTraverse(widget_uri)

            dataManager = ITileDataManager(tile)
            dataManager.delete()


# TODO: implement EditCancelledEvent and EditFinishedEvent
# XXX: we need to leave the view after saving or cancelling editing
class Compose(grok.View):
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def update(self):
        self.context = aq_inner(self.context)
        # XXX: used to lock the object when someone is editing it
        notify(EditBegunEvent(self.context))


# TODO: implement EditCancelledEvent and EditFinishedEvent
# XXX: we need to leave the view after saving or cancelling editing
class LayoutEdit(grok.View):
    grok.context(ICover)
    grok.require('collective.cover.CanEditLayout')

    def update(self):
        self.context = aq_inner(self.context)
        # XXX: used to lock the object when someone is editing it
        notify(EditBegunEvent(self.context))

    def __call__(self):
        if 'export-layout' in self.request and self.can_export_layout():
            name = self.request.get('layout-name', None)
            if name:
                layout = self.context.cover_layout

                registry = getUtility(IRegistry)
                settings = registry.forInterface(ICoverSettings)

                # Store name and layout as unicode.  Note that the
                # name must only contain ascii because it is used as
                # value for a vocabulary.
                name = name.decode('ascii', 'ignore')
                layout = layout.decode('utf-8')
                settings.layouts[name] = layout

        return super(LayoutEdit, self).__call__()

    def can_export_layout(self):
        sm = getSecurityManager()
        portal = api.portal.get()
        # TODO: check permission locally and not in portal context
        return sm.checkPermission('collective.cover: Can Export Layout', portal)

    def layoutmanager_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        grid = getUtility(IGridSystem, name=settings.grid_system)

        return json.dumps({'ncolumns': grid.ncolumns})


class UpdateTileContent(grok.View):

    """Helper browser view to update the content of a tile."""

    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        """Render a tile after populating it with an object."""
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uid = self.request.form.get('uid')
        if tile_type and tile_id and uid:
            catalog = api.portal.get_tool('portal_catalog')
            results = catalog(UID=uid)
            if results:
                obj = results[0].getObject()
                tile = self.context.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))
                tile.populate_with_object(obj)
                # reinstantiate the tile to update its content on AJAX calls
                tile = self.context.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))
                return tile()
        else:
            raise BadRequest('Invalid parameters')


class UpdateTile(grok.View):
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')

        if tile_type and tile_id:
            tile = self.context.restrictedTraverse(tile_type)
            tile_instance = tile[tile_id]
        return tile_instance()


class UpdateListTileContent(grok.View):
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uids = self.request.form.get('uids[]')
        html = ''
        if tile_type and tile_id and uids:
            tile = self.context.restrictedTraverse(tile_type)
            tile_instance = tile[tile_id]
            try:
                tile_instance.replace_with_objects(uids)
                html = tile_instance()
            except:
                # XXX: Pass silently ?
                pass

        # XXX: Calling the tile will return the HTML with the headers, need to
        #      find out if this affects us in any way.
        return html


class RemoveItemFromListTile(grok.View):

    """Helper browser view to remove an object from a list tile."""

    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        """Render a tile after removing an object from it."""
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uid = self.request.form.get('uid')
        if tile_type and tile_id and uid:
            tile = self.context.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))
            if isinstance(tile, ListTile):
                tile.remove_item(uid)
                return tile()
        else:
            raise BadRequest('Invalid parameters')


class DeleteTile(grok.View):
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')

        if tile_type and tile_id:
            tile = self.context.restrictedTraverse(tile_type)
            tile_instance = tile[tile_id]
            tile_instance.delete()
