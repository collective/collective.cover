# -*- coding: utf-8 -*-
from collective.cover.config import PROJECTNAME
from collective.cover.controlpanel import ICoverSettings
from collective.cover.interfaces import ICover
from collective.cover.utils import assign_tile_ids
from five import grok
from plone import api
from plone.dexterity.content import Item
# from plone.indexer import indexer
from plone.registry.interfaces import IRegistry
# from Products.CMFPlone.utils import safe_unicode
from Products.GenericSetup.interfaces import IDAVAware
from zope.component import getUtility
from zope.container.interfaces import IObjectAddedEvent
from zope.interface import implements

import json
import logging

logger = logging.getLogger(PROJECTNAME)


class Cover(Item):

    """A composable page."""

    # XXX: Provide this so Cover items can be imported using the import
    #      content from GS, until a proper solution is found.
    #      ref: http://thread.gmane.org/gmane.comp.web.zope.plone.devel/31799
    implements(IDAVAware)

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
            assert isinstance(layout, list)

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
        """Return a list of tile id the layout.

        :param types: tile types to be filtered; if none, return all tiles
        :type types: str or list
        :returns: a list of tile ids
        """
        return [t['id'] for t in self.get_tiles(types)]


@grok.subscribe(ICover, IObjectAddedEvent)
def assign_id_for_tiles(cover, event):
    if not cover.cover_layout:
        # When versioning, a new cover gets created, so, if we already
        # have a cover_layout stored, do not overwrite it
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)

        layout = settings.layouts.get(cover.template_layout)
        if layout:
            layout = json.loads(layout)
            assign_tile_ids(layout)

            cover.cover_layout = json.dumps(layout)


# SearchAbleText helper
def _get_richtext_value(tile, rich_text):
    """Helper to try and get the normal value of a richtext"""
    text = None
    transforms = api.portal.get_tool('portal_transforms')
    try:
        text = transforms.convert('html_to_text', rich_text).getData()
    except UnicodeError:
        try:
            rich_text = rich_text.encode('utf-8')
            text = transforms.convert('html_to_text', rich_text).getData()
        except UnicodeError:
            pass
    return text


def _get_tiles(obj, section, tiles_text_list=[]):
    """Little bit of recursive loving. Parytly copied from
       layout.py render_section function"""

    if 'type' in section:
        if section['type'] in [u'row', u'group']:
            for sec in section.get('children', []):
                tiles_text_list = _get_tiles(obj, sec, tiles_text_list)
        if section['type'] == u'tile':
            tile_type = section.get('tile-type')
            if tile_type == u'collective.cover.richtext':
                tile_id = section.get(u'id')
                path = '{0}/{1}'.format(str(tile_type), str(tile_id))
                tile = obj.restrictedTraverse(path)
                if tile.data.get('text'):
                    rich_text = tile.data.get('text').output
                    text = _get_richtext_value(tile, rich_text)
                    tiles_text_list.append(text)
    elif type(section) == list:
        for sec in section:
            tiles_text_list = _get_tiles(obj, sec, tiles_text_list)

    return tiles_text_list


# @indexer(ICover)
# def searchableText(obj):
#     """Indexer to add richtext tiles text to SearchableText"""
#     cover_layout = obj.cover_layout
#     searchable = obj.Title()
#     searchable = u'{0} {1}'.format(searchable, safe_unicode(obj.Description()))
#     if cover_layout:
#         layout = json.loads(cover_layout)
#         tiles_text_list = _get_tiles(obj, layout)

#         searchable = obj.Title()
#         description = safe_unicode(obj.Description())
#         searchable = u'{0} {1}'.format(searchable, description)
#         for text in tiles_text_list:
#             searchable = u'{0} {1}'.format(searchable, safe_unicode(text))

#     return searchable

# grok.global_adapter(searchableText, name='SearchableText')
