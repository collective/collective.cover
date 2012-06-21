# -*- coding: utf-8 -*-

import json
import sys
import string

from random import choice
from sha import sha
from pyquery import PyQuery

from five import grok

from zope.annotation.interfaces import IAnnotations

from zope.app.container.interfaces import IObjectAddedEvent

from zope.interface import Interface
from zope.component import getAdapter
from zope.component import getUtility

from plone.dexterity.utils import createContentInContainer

from plone.directives import dexterity, form

from plone.registry.interfaces import IRegistry

from plone.tiles.interfaces import ITileDataManager

from plone.uuid.interfaces import IUUIDGenerator

from Products.CMFPlone.interfaces import INonStructuralFolder

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext

from collective.composition.controlpanel import ICompositionSettings


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


class LayoutEdit(grok.View):
    grok.context(IComposition)
    grok.require('cmf.ModifyPortalContent')


class UpdateTileContent(grok.View):
    grok.context(IComposition)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        pc = getToolByName(self.context, 'portal_catalog')

        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uid = self.request.form.get('uid')

        if tile_type and tile_id and uid:

            tile = self.context.restrictedTraverse(tile_type)

            tile_instance = tile[tile_id]

            results = pc(UID=uid)
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


class DeleteTile(grok.View):
    grok.context(IComposition)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        pc = getToolByName(self.context, 'portal_catalog')

        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')

        if tile_type and tile_id:

            tile = self.context.restrictedTraverse(tile_type)

            tile_instance = tile[tile_id]

            tile_instance.delete()


def assign_tile_ids(layout):
    """
    This function takes a dict, and it will recursively traverse it and assign
    sha-hashed ids so we are pretty sure they are unique among them
    """

    for elem in layout:
        if elem['type'] == u'tile':
            random_string = ''
            for i in xrange(100):
                random_string += choice(string.letters)
            elem['id'] = sha(random_string).hexdigest()
        else:
            children = elem['children']
            assign_tile_ids(children)


@grok.subscribe(IComposition, IObjectAddedEvent)
def assign_id_for_tiles(composition, event):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICompositionSettings)

    layout = settings.layouts[composition.template_layout]

    layout = json.loads(layout)

    assign_tile_ids(layout)

    composition.composition_layout = json.dumps(layout)
