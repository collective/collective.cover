# -*- coding: utf-8 -*-
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


class Cover(Item):
    """
    """
    # XXX: Provide this so Cover items can be imported using the import
    #      content from GS, until a proper solution is found.
    #      ref: http://thread.gmane.org/gmane.comp.web.zope.plone.devel/31799
    implements(IDAVAware)


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
