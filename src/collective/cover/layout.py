# -*- coding: utf-8 -*-

import json
import uuid

from Acquisition import aq_inner

from five import grok

from zope.component import queryUtility, getMultiAdapter
from zope.schema.interfaces import IVocabularyFactory

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from plone.principalsource.source import GroupsVocabularyFactory

from collective.cover.content import ICover
from collective.cover.utils import assign_tile_ids


class PageLayout(grok.View):
    """
    Renders a layout for the cover object.
    """
    grok.context(ICover)
    grok.name('layout')
    grok.require('zope2.View')

    pagelayout = ViewPageTemplateFile('layout_templates/pagelayout.pt')
    row = ViewPageTemplateFile('layout_templates/row.pt')
    group = ViewPageTemplateFile('layout_templates/group.pt')
    tile = ViewPageTemplateFile('layout_templates/tile.pt')
    generalmarkup = ViewPageTemplateFile('layout_templates/generalmarkup.pt')

    def get_layout(self, mode):
        layout = json.loads(self.context.cover_layout)

        if mode == 'view' or mode == 'compose':
            grid_plug = getMultiAdapter((self.context, self.request),
                                        name=u'grid_plug')

            grid_plug.transform(layout)
        else:
            self.grid_layout_edit(layout)

        return layout

    def grid_layout_edit(self, layout):
        for element in layout:
            if 'type' in element:
                if element['type'] == 'row':
                    element['class'] = 'cover-row'

                if element['type'] == 'group':
                    element['class'] = 'cover-column'

                if element['type'] == 'tile':
                    element['class'] = 'cover-tile'

                if 'children' in element:
                    self.grid_layout_edit(element['children'])

    def render_section(self, section, mode):
        if 'type' in section:
            if section['type'] == u'row':
                return self.row(section=section, mode=mode)
            if section['type'] == u'group':
                return self.group(section=section, mode=mode)
            if section['type'] == u'tile':
                return self.tile(section=section, mode=mode)
        else:
            return self.generalmarkup(section=section, mode=mode)

    def is_user_allowed_in_group(self):
        return True

    def tile_is_configurable(self, tile_type):
        tile = self.context.restrictedTraverse(str(tile_type))
        return tile.is_configurable

    def tile_is_droppable(self, tile_type):
        tile = self.context.restrictedTraverse(str(tile_type))
        return tile.is_droppable

    def tile_is_editable(self, tile_type):
        tile = self.context.restrictedTraverse(str(tile_type))
        return tile.is_editable

    def can_compose_tile_class(self, tile_type, tile_id):
        tile = self.context.restrictedTraverse("%s/%s" % (str(tile_type), str(tile_id)))
        if not tile.isAllowedToEdit():
            return "disabled"
        else:
            return ""

    def render_view(self):
        # XXX: There *must* be a better way of doing this, maybe write it
        #      in the request ? sending it as parameter is way too ugly
        return self.pagelayout(mode="view")

    def render_compose(self):
        # XXX: There *must* be a better way of doing this, maybe write it
        #      in the request ? sending it as parameter is way too ugly
        return self.pagelayout(mode="compose")

    def render_layout_edit(self):
        # XXX: There *must* be a better way of doing this, maybe write it
        #      in the request ? sending it as parameter is way too ugly
        return self.pagelayout(mode="layout_edit")

    def accepted_ct_for_tile(self, tile_type):
        tile = self.context.restrictedTraverse(str(tile_type))
        accepted_ct = tile.accepted_ct()

        return json.dumps(accepted_ct)


class LayoutSave(grok.View):
    grok.context(ICover)
    grok.name('save_layout')
    grok.require('zope2.View')

    def save(self):
        cover_layout = self.request.get('cover_layout')

        layout = json.loads(cover_layout)

        assign_tile_ids(layout, override=False)

        cover_layout = json.dumps(layout)

        self.context.cover_layout = cover_layout
        self.context.reindexObject()

        return cover_layout

    def render(self):
        self.save()
        return 'saved'


class TileSelect(grok.View):
    grok.context(ICover)
    grok.name('tile_select')
    grok.require('zope2.View')

    def update(self):
        self.context = aq_inner(self.context)
        name = 'collective.cover.AvailableTiles'
        available_tiles = queryUtility(IVocabularyFactory, name)
        # the view is expecting a dictionary of "tile types"
        self.tiles = [{'tile_type': name.value}
                      for name in available_tiles(self.context)]


class UidGetter(grok.View):
    grok.context(ICover)
    grok.name('uid_getter')
    grok.require('zope2.View')

    def render(self):
        return uuid.uuid4().hex


class GroupSelect(grok.View):
    grok.context(ICover)
    grok.name('group_select')
    grok.require('zope2.View')

    def update(self):
        self.groups = GroupsVocabularyFactory(self.context)
        if "groups[]" in self.request.keys():
            groups = self.request["groups[]"]
            tile_len = int(self.request["tile_len"])
            i = 0
            while(i < tile_len):
                tile_type = self.request["tiles[%s][type]" % i]
                tile_id = self.request["tiles[%s][id]" % i]
                tile = self.context.restrictedTraverse("%s/%s" % (tile_type, tile_id))
                tile.setAllowedGroupsForEdit(groups)
                i += 1


class GridPlug(grok.View):
    grok.context(ICover)
    grok.name('grid_plug')
    grok.require('zope2.View')

    row_class = 'row'
    column_class = 'cell'

    def transform(self, layout):
        for element in layout:
            if 'type' in element:
                if element['type'] == 'row':
                    element['class'] = self.row_class
                    if 'children' in element:
                        self.transform(self.columns_formater(element['children']))
                if element['type'] == 'group' and 'children' in element:
                    self.transform(element['children'])

                if element['type'] == 'tile':
                    element['class'] = 'tile'

    def columns_formater(self, columns):
        #this formater works for deco, but you can implemente a custom one, for you grid system
        w = 'width-'
        p = 'position-'
        offset = 0
        for column in columns:
            width = column['data']['column-size'] if 'data' in column else 1
            column['class'] = self.column_class + ' ' + (w + str(width)) + ' ' + (p + str(offset))
            offset = offset + width
        return columns

    def render(self):
        return self


## EXAMPLE of a usagge for a custom grid system, in this case, boostrap
# class GridPlug(grok.View):
#     grok.context(ICover)
#     grok.name('grid_plug')
#     grok.require('zope2.View')
#     grok.layer(YOURLAYERINTERFACE)

#     row_class = 'row'
#     column_class = 'column'

#     def columns_formater(self, columns):
#         #this formater works for deco, but you can implemente a custom one, for you grid system
#         w = 'span'

#         for column in columns:
#             width = column['data']['column-size']
#             column['class'] = self.column_class + ' ' + (w + str(width))

#         return columns
