# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.cover.tiles.list import IListTile
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.events import EditBegunEvent
from plone.dexterity.utils import createContentInContainer
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDGenerator
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.event import notify
from zope.interface import implementer

import json


# TODO: implement EditCancelledEvent and EditFinishedEvent
# XXX: we need to leave the view after saving or cancelling editing
@implementer(IBlocksTransformEnabled)
class Compose(BrowserView):

    index = ViewPageTemplateFile('templates/compose.pt')

    def setup(self):
        self.context = aq_inner(self.context)
        # XXX: used to lock the object when someone is editing it
        notify(EditBegunEvent(self.context))

    def render(self):
        return self.index()

    def __call__(self):
        self.setup()
        return self.render()


class AddCTWidget(BrowserView):

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

    def __call__(self):
        return self.render()


class AddTileWidget(BrowserView):

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

    def __call__(self):
        return self.render()


class SetWidgetMap(BrowserView):

    def render(self):
        widget_map = self.request.get('widget_map')
        remove = self.request.get('remove', None)
        self.context.set_widget_map(widget_map, remove)
        return json.dumps('success')

    def __call__(self):
        return self.render()


class UpdateWidget(BrowserView):

    def render(self):
        widget_id = self.request.get('wid')
        if widget_id in self.context:
            return self.context[widget_id].render()
        else:
            return 'Widget does not exist'

    def __call__(self):
        return self.render()


class RemoveTileWidget(BrowserView):
    # XXX: This should be part of the plone.app.tiles package or similar

    index = ViewPageTemplateFile('templates/removetilewidget.pt')

    def render(self):
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
        return self.index()

    def __call__(self):
        return self.render()


class UpdateTileContent(BrowserView):

    """Helper browser view to update the content of a tile."""

    def render(self):
        """Render a tile after populating it with an object."""
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uuid = self.request.form.get('uuid')
        if tile_type and tile_id and uuid:
            catalog = api.portal.get_tool('portal_catalog')
            results = catalog(UID=uuid)
            if results:
                obj = results[0].getObject()
                tile = self.context.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))
                tile.populate_with_object(obj)
                # reinstantiate the tile to update its content on AJAX calls
                tile = self.context.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))
                return tile()
        else:
            raise BadRequest('Invalid parameters')

    def __call__(self):
        return self.render()


class MoveTileContent(BrowserView):

    """Helper browser view to move the content from one tile to another."""

    def _move_all_content(self, origin_tile, target_tile):
        """Move all content from one tile to another tile"""
        # copy data
        origin_dmgr = ITileDataManager(origin_tile)
        origin_data = origin_dmgr.get()
        if origin_data.get('uuids', None) is None:
            return
        target_dmgr = ITileDataManager(target_tile)
        target_dmgr.set(origin_dmgr.get())
        # remove origin tile
        origin_dmgr.delete()

    def _move_selected_content(self, origin_tile, target_tile, obj):
        """Move selected content from one tile to another tile"""
        target_tile.populate_with_object(obj)
        if IListTile.providedBy(origin_tile):
            uuid = IUUID(obj)
            origin_tile.remove_item(uuid)
        else:
            origin_dmgr = ITileDataManager(origin_tile)
            origin_data = origin_dmgr.get()
            target_dmgr = ITileDataManager(target_tile)
            target_data = target_dmgr.get()
            for k, v in origin_data.iteritems():
                if k in target_data and not k.startswith('uuid') and v is not None:
                    target_data[k] = v
            target_dmgr.set(target_data)
            origin_dmgr.delete()

    def render(self):
        """Render a tile after populating it with an object."""
        origin_type = self.request.form.get('origin-type')
        origin_id = self.request.form.get('origin-id')
        target_type = self.request.form.get('target-type')
        target_id = self.request.form.get('target-id')
        if not all([origin_type, origin_id, target_type, target_id]):
            raise BadRequest('Invalid parameters')
        origin_tile = self.context.restrictedTraverse('{0}/{1}'.format(origin_type, origin_id))
        target_tile = self.context.restrictedTraverse('{0}/{1}'.format(target_type, target_id))
        uuid = self.request.form.get('uuid')
        obj = uuidToObject(uuid)
        if obj is None:
            self._move_all_content(origin_tile, target_tile)
        else:
            self._move_selected_content(origin_tile, target_tile, obj)
        # reinstantiate the tile to update its content on AJAX calls
        target_tile = self.context.restrictedTraverse('{0}/{1}'.format(target_type, target_id))
        return target_tile()

    def __call__(self):
        return self.render()


class UpdateListTileContent(BrowserView):

    def render(self):
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uuids = self.request.form.get('uuids[]')
        if type(uuids) is not list:
            uuids = [uuids]
        html = ''
        if tile_type and tile_id and uuids:
            tile = self.context.restrictedTraverse(tile_type)
            tile_instance = tile[tile_id]
            try:
                tile_instance.replace_with_uuids(uuids)
                html = tile_instance()
            except:  # FIXME: B901 blind except: statement
                # XXX: Pass silently ?
                pass

        # XXX: Calling the tile will return the HTML with the headers, need to
        #      find out if this affects us in any way.
        return html

    def __call__(self):
        return self.render()


class RemoveItemFromListTile(BrowserView):

    """Helper browser view to remove an object from a list tile."""

    def render(self):
        """Render a tile after removing an object from it."""
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uuid = self.request.form.get('uuid')
        if tile_type and tile_id and uuid:
            tile = self.context.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))
            if IListTile.providedBy(tile):
                tile.remove_item(uuid)
                # reinstantiate the tile to update its content on AJAX calls
                tile = self.context.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))
                return tile()
        else:
            raise BadRequest('Invalid parameters')

    def __call__(self):
        return self.render()


class DeleteTile(BrowserView):

    def render(self):
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')

        if tile_type and tile_id:
            tile = self.context.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))
            tile.delete()

    def __call__(self):
        return self.render()
