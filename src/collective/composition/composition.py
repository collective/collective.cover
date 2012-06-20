# -*- coding: utf-8 -*-

import sys

import json

from five import grok
from plone.directives import dexterity, form

from zope.interface import Interface
from zope.component import getAdapter
from zope.component import getUtility

from Products.CMFPlone.interfaces import INonStructuralFolder
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext
from plone.dexterity.utils import createContentInContainer

from pyquery import PyQuery

from plone.uuid.interfaces import IUUIDGenerator
from plone.tiles.interfaces import ITileDataManager


class IComposition(form.Schema):
    """
    Composable page
    """
    form.model("models/composition.xml")


class ICompositionFragment(Interface):
    """
    Main interface for fragments
    """


class Composition(dexterity.Container):
    grok.implements(IComposition, INonStructuralFolder)

    widget_map = {}

    @property
    def current_layout(self):
        layout_name = self.composition_layout
        layout = getAdapter((self,), ICompositionLayout, name=layout_name)
        return layout

    def get_ct_widgets(self):
        types_tool = getToolByName(self, "portal_types")
        types = types_tool.listTypeInfo()
        available = []
        for type_info in types:
            dotted = getattr(type_info, 'klass', None)
            if not dotted:
                continue
            package, klass = dotted.rsplit('.', 1)
            try:
                __import__(package)
            except ImportError:
                continue
            klass = getattr(sys.modules[package], klass, None)
            if not ICompositionFragment.implementedBy(klass):
                continue
            expression = Expression(type_info.icon_expr)
            expression_context = getExprContext(self)
            icon = expression(expression_context)
            available.append({'portal_type': type_info.id,
                              'icon': icon,
                              'title': type_info.title,
                              'description': type_info.description})
        return available

    def get_tile_widgets(self):

        available = []
        #TODO: Think of a way to register available tiles
        #      And from here, just ask which tiles are available for this
        #      context
        available.append({'tile_type': "collective.composition.richtext",
                          'icon': '',
                          'title': "Rich text tile",
                          'description': ("A persistent tile which allows to "
                                          "create content using a WYSIWYG "
                                          "editor")})

        available.append({'tile_type': "collective.composition.container",
                          'icon': '',
                          'title': "Container tile",
                          'description': ("A tile wich can contain other "
                                          "tiles")})

        return available

    def available_widgets(self):
        available = []
        available += self.get_ct_widgets()
        available += self.get_tile_widgets()

        return available

    def set_widget_map(self, widget_map, remove=None):
        layout = self.current_layout
        columns = layout.columns
        new_map = {}
        for column in columns:
            new_map[column] = []
        widget_map = widget_map.split('&')
        annotations = IAnnotations(self)
        current_tiles = annotations.get('current_tiles', {})
        for widget in widget_map:
            key, value = widget.split(':')
            if remove is not None:
                remove_col, remove_val = remove.split(':')
                if remove_col == key and remove_val == value:
                    # If this was a tile, then remove it from the annotations
                    if value in current_tiles:
                        del current_tiles[value]
                        annotations['current_tiles'] = current_tiles
                    continue
            new_map[key].append(value)
        self.widget_map = new_map

    def render(self, edit=False):
        layout = self.current_layout
        rendered = layout.render()
        if not edit:
            widget_markup = """
            <div id="%(wid)s" class="view-widget %(class)s">
              %(content)s
            </div>
            """
        else:
            widget_markup = """
            <div id="%(wid)s" class="widget %(class)s">
              <div class="widget-head"><h3>%(title)s</h3></div>
              <div class="widget-content">%(content)s</div>
            </div>
            """
        pq = PyQuery(rendered)
        for column, addwidgets in self.widget_map.items():
            for addwidget in addwidgets:
                try:
                    widget = self[addwidget]
                    widget_info = {'col': column,
                                   'wid': addwidget,
                                   'title': widget.title,
                                   'class': 'ct',
                                   'content': widget.render(),
                                   'url': widget.absolute_url()
                                   }
                except KeyError:
                    # This might be a tile
                    annotations = IAnnotations(self)
                    current_tiles = annotations.get('current_tiles', {})
                    if addwidget in current_tiles:
                        widget_type = current_tiles[addwidget]['type']
                        context_url = self.absolute_url()
                        widget_title = current_tiles[addwidget].get('title',
                                                                    '')
                        widget_url = '%s/@@%s/%s' % (context_url,
                                                     widget_type,
                                                     addwidget)
                        widget_render = '<div data-tile="%s" />' % widget_url
                        widget_info = {'col': column,
                                       'wid': addwidget,
                                       'title': widget_title,
                                       'class': 'tile',
                                       'content': widget_render,
                                       'url': widget_url}

                pq('#%s' % column).append(widget_markup % widget_info)

        return pq.outerHtml()


class View(grok.View):
    grok.context(IComposition)
    grok.require('zope2.View')
    grok.name('view')


class AddCTWidget(grok.View):
    grok.context(IComposition)
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
    grok.context(IComposition)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        uuid = getUtility(IUUIDGenerator)
        widget_type = self.request.get('widget_type')
        widget_title = self.request.get('widget_title')
        column_id = self.request.get('column_id')

        id = uuid()
        context_url = self.context.absolute_url()
        widget_url = '%s/@@%s/%s' % (context_url, widget_type, id)

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
    grok.context(IComposition)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        widget_map = self.request.get('widget_map')
        remove = self.request.get('remove', None)
        self.context.set_widget_map(widget_map, remove)
        return json.dumps('success')


class UpdateWidget(grok.View):
    grok.context(IComposition)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        widget_id = self.request.get('wid')
        if widget_id in self.context:
            return self.context[widget_id].render()
        else:
            return 'Widget does not exist'


class RemoveTileWidget(grok.View):
    # XXX: This should be part of the plone.app.tiles package or similar
    grok.context(IComposition)
    grok.require('cmf.ModifyPortalContent')
    grok.name("removetilewidget")

    def __call__(self):
        template = self.template
        if 'form.submitted' not in self.request:
            return template.render(self)

        annotations = IAnnotations(self.context)
        current_tiles = annotations.get('current_tiles', {})
        tile_id = self.request.get('wid', None)

        if tile_id in current_tiles:
            widget_type = current_tiles[tile_id]['type']
            #Let's remove all traces of the value stored in the tile
            tile = self.context.restrictedTraverse(
                                        '@@%s/%s' % (widget_type, tile_id,))

            dataManager = ITileDataManager(tile)
            dataManager.delete()


class Compose(grok.View):
    grok.context(IComposition)
    grok.require('cmf.ModifyPortalContent')

    def render_context_menus(self):
        widget_template = """
                {label:'%(title)s',
                 icon:'%(icon)s',
                 action:function() { Composition.addCTWidget('#*slot*', '%(portal_type)s', '%(title)s'); }
                }"""
        tile_widget_template = """
                {label:'%(title)s',
                 icon:'%(icon)s',
                 action:function() { Composition.addTileWidget('#*slot*', '%(tile_type)s', '%(title)s'); }
                }"""
        widget_list = []
        tile_widget_list = []
        for widget in self.context.available_widgets():
            if 'portal_type' in widget:
                widget_list.append(widget_template % widget)
            if 'tile_type' in widget:
                tile_widget_list.append(tile_widget_template % widget)
        ct_widgets = ",".join(widget_list)
        tile_widgets = ",".join(tile_widget_list)
        menu_template = """
            $('#%s').contextPopup({
              ct_title: 'Add CT Widgets',
              ct_items: [
              %s
              ],
              tile_title: 'Add Tile Widgets',
              tile_items: [
              %s
              ]});"""
        menus = """
            jQuery(function($) {"""
        for column in self.context.current_layout.columns:
            menu = menu_template % (column, ct_widgets, tile_widgets)
            menu = menu.replace('*slot*', column)
            menus += menu
        menus += """
            })"""
        return menus

    def render_widget_initialization(self):
        init = """
            jQuery(function($) {"""
        for column, addwidgets in self.context.widget_map.items():
            for addwidget in addwidgets:
                try:
                    widget = self.context[addwidget]
                    init += ("Composition.addCTWidgetControls('%s', '%s');\n" %
                             (addwidget, widget.absolute_url()))
                except KeyError:
                    # If we are here, means either we have invalid data or
                    # this might be a tile, let's see
                    annotations = IAnnotations(self.context)
                    current_tiles = annotations.get('current_tiles', {})
                    if addwidget in current_tiles:
                        widget_type = current_tiles[addwidget]['type']
                        context_url = self.context.absolute_url()
                        widget_url = '%s/@@%s/%s' % (context_url,
                                                     widget_type,
                                                     addwidget)
                        init += ("Composition.addTileWidgetControls"
                                 "('%s', '%s');\n" %
                                 (addwidget, widget_url))

        init += """
            Composition.makeSortable();
            })"""
        return init


class UpdateTileContent(grok.View):
    grok.context(IComposition)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        pc = getToolByName(self.context, 'portal_catalog')

        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uuid = self.request.form.get('uuid')

        if tile_type and tile_id and uuid:

            tile = self.context.restrictedTraverse(tile_type)

            tile_instance = tile[tile_id]

            results = pc(UID=uuid)
            if results:
                obj = results[0].getObject()

                try:
                    tile_instance.populate_with_object(obj)
                except:
                    # XXX: Pass silently ?
                    pass

        # XXX: Calling the tile will return the HTML with the headers, need to
        #      find out if this affects us in any way.
        return tile_instance()
