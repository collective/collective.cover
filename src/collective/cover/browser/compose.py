# -*- coding: utf-8 -*-
from collective.cover.tiles.list import IListTile
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.events import EditBegunEvent
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest
from zope.event import notify
from zope.interface import implementer


# TODO: implement EditCancelledEvent and EditFinishedEvent
#       we need to leave the view after saving or cancelling editing
@implementer(IBlocksTransformEnabled)
class Compose(BrowserView):

    """Compose Tab."""

    index = ViewPageTemplateFile('templates/compose.pt')

    def __call__(self):
        # lock the object when someone is editing it
        notify(EditBegunEvent(self.context))
        return self.index()


class UpdateTileContent(BrowserView):

    """Helper browser view to update the content of a tile."""

    def setup(self):
        self.tile_type = self.request.form.get('tile-type')
        self.tile_id = self.request.form.get('tile-id')
        self.uuid = self.request.form.get('uuid')

    def render(self):
        """Render a tile after populating it with an object."""
        if not all((self.tile_type, self.tile_id, self.uuid)):
            raise BadRequest('Invalid parameters')

        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(UID=self.uuid)
        assert len(results) in (0, 1)
        if results:
            obj = results[0].getObject()
            path = '{0}/{1}'.format(self.tile_type, self.tile_id)
            tile = self.context.restrictedTraverse(path)
            tile.populate_with_object(obj)
            # reinstantiate tile to update rendering with new data
            tile = self.context.restrictedTraverse(path)
            return tile()

    def __call__(self):
        self.setup()
        # avoid caching the response on intermediate proxies
        # as this is a GET request, a misconfiguration could
        # result on outdated content being rendered
        self.request.response.setHeader('Cache-Control', 'no-cache')
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

    def setup(self):
        self.origin_type = self.request.form.get('origin-type')
        self.origin_id = self.request.form.get('origin-id')
        self.target_type = self.request.form.get('target-type')
        self.target_id = self.request.form.get('target-id')

    def render(self):
        """Render a tile after populating it with an object."""
        if not all((self.origin_type, self.origin_id, self.target_type, self.target_id)):
            raise BadRequest('Invalid parameters')

        origin_tile = self.context.restrictedTraverse(
            '{0}/{1}'.format(self.origin_type, self.origin_id))
        target_tile = self.context.restrictedTraverse(
            '{0}/{1}'.format(self.target_type, self.target_id))
        uuid = self.request.form.get('uuid')
        obj = uuidToObject(uuid)
        if obj is None:
            self._move_all_content(origin_tile, target_tile)
        else:
            self._move_selected_content(origin_tile, target_tile, obj)
        return target_tile()

    def __call__(self):
        self.setup()
        return self.render()


class UpdateListTileContent(BrowserView):

    """Helper browser view to update the content of a list based tile."""

    def setup(self):
        self.tile_type = self.request.form.get('tile-type')
        self.tile_id = self.request.form.get('tile-id')
        self.uuids = self.request.form.get('uuids[]', [])
        if type(self.uuids) is not list:
            self.uuids = [self.uuids]

    def render(self):
        if not all((self.tile_type, self.tile_id, self.uuids)):
            return u''

        tile = self.context.restrictedTraverse(self.tile_type)
        tile_instance = tile[self.tile_id]
        tile_instance.replace_with_uuids(self.uuids)
        return tile_instance()

    def __call__(self):
        self.setup()
        return self.render()


class RemoveItemFromListTile(BrowserView):

    """Helper browser view to remove an object from a list tile."""

    def setup(self):
        self.tile_type = self.request.form.get('tile-type')
        self.tile_id = self.request.form.get('tile-id')
        self.uuid = self.request.form.get('uuid')

    def render(self):
        """Render a tile after removing an object from it."""
        if not all((self.tile_type, self.tile_id, self.uuid)):
            raise BadRequest('Invalid parameters')

        path = '{0}/{1}'.format(self.tile_type, self.tile_id)
        tile = self.context.restrictedTraverse(path)
        if IListTile.providedBy(tile):
            tile.remove_item(self.uuid)
            return tile()

    def __call__(self):
        self.setup()
        return self.render()


class DeleteTile(BrowserView):

    """Helper browser view to remove a tile."""

    def setup(self):
        self.tile_type = self.request.form.get('tile-type')
        self.tile_id = self.request.form.get('tile-id')

    def render(self):
        if self.tile_type and self.tile_id:
            path = '{0}/{1}'.format(self.tile_type, self.tile_id)
            tile = self.context.restrictedTraverse(path)
            tile.delete()

    def __call__(self):
        self.setup()
        return self.render()
