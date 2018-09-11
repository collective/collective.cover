# -*- coding: utf-8 -*-
from collective.cover.behaviors.interfaces import IRefresh
from collective.cover.config import ANNOTATION_PREFIXES
from collective.cover.config import PROJECTNAME
from collective.cover.interfaces import ICover
from collective.cover.interfaces import ISearchableText
from collective.cover.tiles.list import IListTile
from collective.cover.tiles.richtext import IRichTextTile
from plone.app.linkintegrity.handlers import getObjectsFromLinks
from plone.app.linkintegrity.parser import extractLinks
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.content import Item
from plone.indexer import indexer
from plone.tiles.interfaces import ITileDataManager
from Products.CMFPlone.utils import safe_unicode
from zope.annotation import IAnnotations
from zope.component import queryAdapter

import json
import logging


logger = logging.getLogger(PROJECTNAME)


class Cover(Item):
    """A composable page."""

    @property
    def refresh(self):
        """Return the value of the enable_refresh field if the IRefresh
        behavior is applied to the object, or False if not.

        :returns: True if refresh of the current page is enabled
        :rtype: bool
        """
        return self.enable_refresh if IRefresh.providedBy(self) else False

    def get_tiles(self, types=None, layout=None):
        """Traverse the layout tree and return a list of tiles on it.

        :param types: tile types to be filtered; if none, return all tiles
        :type types: str or list
        :param layout: a JSON object describing sub-layout (internal use)
        :type layout: list
        :returns: a list of tiles; each tile is described as {id, type}
        """
        filter = types is not None
        if filter and isinstance(types, str):
            types = [types]

        if layout is None:
            # normal processing, we use the object's layout
            try:
                layout = json.loads(self.cover_layout)
            except TypeError:
                # XXX: we are probably running tests so just return an
                #      empty layout; maybe we should fix this in other
                #      way: cover_layout should be initiated at
                #      object's creation and not at LayoutSave view
                logger.debug('cover_layout attribute was empty')
                layout = []
        else:
            # we are recursively processing the layout
            assert isinstance(layout, list)  # nosec

        tiles = []
        for e in layout:
            if e['type'] == 'tile':
                if filter and e['tile-type'] not in types:
                    continue
                tiles.append(dict(id=e['id'], type=e['tile-type']))
            if 'children' in e:
                tiles.extend(self.get_tiles(types, e['children']))
        return tiles

    def list_tiles(self, types=None):
        """Return a list of tile id on the layout.

        :param types: tile types to be filtered; if none, return all tiles
        :type types: string or list
        :returns: a list of tile ids
        :rtype: list of strings
        """
        return [t['id'] for t in self.get_tiles(types)]

    def get_tile_type(self, id):
        """Get the type of the tile defined by the id.

        :param id: id of the tile we want to get its type
        :type id: string
        :returns: the tile type
        :rtype: string
        :raises ValueError: if the tile does not exists
        """
        tile = [t for t in self.get_tiles() if t['id'] == id]
        assert len(tile) in (0, 1)  # nosec
        if len(tile) == 0:
            raise ValueError
        return tile[0]['type']

    def get_tile(self, tile_id):
        """Get the tile defined by id.

        :param tile_id: tile_id of the tile we want to get
        :type tile_id: string
        :returns: a tile
        :rtype: PersistentTile instance
        """
        tile_type = str(self.get_tile_type(tile_id))
        tile_id = str(tile_id)
        return self.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))

    def set_tile_data(self, tile_id, **data):
        """Set data attributes on the tile defined by id.

        :param tile_id: tile_id of the tile we want to modify its data
        :type tile_id: string
        :param data: a dictionary of attributes we want to set on the tile
        :type data: dictionary
        """
        tile = self.get_tile(tile_id)
        data_mgr = ITileDataManager(tile)
        data_mgr.set(data)

    def get_referenced_objects(self):
        """Get referenced objects from cover object.

        :returns: a set of objects referenced
        :rtype: set of objects
        """
        refs = set()
        for tile_uuid in self.list_tiles():
            tile = self.get_tile(tile_uuid)
            uuid = tile.data.get('uuid', None)
            if uuid is not None:
                refs |= set([uuidToObject(uuid)])
            if IListTile.providedBy(tile):
                uuids = tile.data.get('uuids', [])
                if uuids is None:
                    continue
                for uuid in uuids:
                    refs |= set([uuidToObject(uuid)])
            elif IRichTextTile.providedBy(tile):
                value = tile.data.get('text')
                if value is None:
                    continue
                value = value.raw
                links = extractLinks(value)
                refs |= getObjectsFromLinks(self, links)
        return refs

    def purge_deleted_tiles(self):
        """Purge annotations of tiles that are no longer referenced on
        the layout.
        """
        layout_tiles = self.list_tiles()
        annotations = IAnnotations(self)

        for key in annotations:
            if not key.startswith(ANNOTATION_PREFIXES):
                continue

            # XXX: we need to remove tile annotations at low level as
            #      there's no information available on the tile type
            #      (it's no longer in the layout and we can only infer
            #      its id); this could lead to issues in the future if
            #      a different storage is used (see plone.tiles code)
            tile_id = key.split('.')[-1]
            if tile_id not in layout_tiles:
                del annotations[key]


@indexer(ICover)
def searchableText(obj):
    """Return searchable text to be used as indexer. Includes id, title,
    description and text from Rich Text tiles."""
    text_list = []
    tiles = obj.get_tiles()
    for tile in tiles:
        tile_obj = obj.restrictedTraverse('@@{0}/{1}'.format(tile['type'], tile['id']))
        searchable = queryAdapter(tile_obj, ISearchableText)
        if searchable:
            text_list.append(searchable.SearchableText())
    tiles_text = u' '.join(text_list)
    searchable_text = [safe_unicode(entry) for entry in (
        obj.id,
        obj.Title(),
        obj.Description(),
        tiles_text,
    ) if entry]
    searchable_text = u' '.join(searchable_text)
    return searchable_text
