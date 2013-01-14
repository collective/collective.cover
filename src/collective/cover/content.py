# -*- coding: utf-8 -*-

import json

from Acquisition import aq_inner

from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.event import notify

from five import grok
from zope.app.container.interfaces import IObjectAddedEvent

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonStructuralFolder

from plone.dexterity.events import EditBegunEvent
#from plone.dexterity.events import EditCancelledEvent
#from plone.dexterity.events import EditFinishedEvent
from plone.dexterity.utils import createContentInContainer
from plone.directives import dexterity, form
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUIDGenerator

from collective.cover.controlpanel import ICoverSettings
from collective.cover.utils import assign_tile_ids

grok.templatedir('templates')


class ICover(form.Schema):
    """
    Composable page
    """
    form.model("models/cover.xml")


# FIXME: we must inherit from dexterity.Item but we have to fix issue #48
class Cover(dexterity.Container):
    """
    """
    grok.implements(ICover, INonStructuralFolder)


class View(grok.View):
    grok.context(ICover)
    grok.require('zope2.View')
    grok.name('view')


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
            widget_uri = '@@%s/%s' % (widget_type, tile_id,)
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
    grok.require('cmf.ModifyPortalContent')

    def update(self):
        self.context = aq_inner(self.context)
        # XXX: used to lock the object when someone is editing it
        notify(EditBegunEvent(self.context))

    def __call__(self):
        if 'export-layout' in self.request:
            name = self.request.get('layout-name', None)
            if name:
                layout = self.context.cover_layout

                registry = getUtility(IRegistry)

                settings = registry.forInterface(ICoverSettings)

                settings.layouts[name] = unicode(layout)

        return super(LayoutEdit, self).__call__()


class UpdateTileContent(grok.View):
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        pc = getToolByName(self.context, 'portal_catalog')

        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uid = self.request.form.get('uid')

        html = ""
        if tile_type and tile_id and uid:

            tile = self.context.restrictedTraverse(tile_type)
            tile_instance = tile[tile_id]

            results = pc(UID=uid)
            if results:
                obj = results[0].getObject()

                try:
                    tile_instance.populate_with_object(obj)
                    html = tile_instance()
                except:
                    # XXX: Pass silently ?
                    pass

            # XXX: Calling the tile will return the HTML with the headers, need to
            #      find out if this affects us in any way.
        return html


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
        html = ""
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
    grok.context(ICover)
    grok.require('cmf.ModifyPortalContent')

    def render(self):
        tile_type = self.request.form.get('tile-type')
        tile_id = self.request.form.get('tile-id')
        uid = self.request.form.get('uid')
        html = ""
        if tile_type and tile_id and uid:
            tile = self.context.restrictedTraverse(tile_type)
            tile_instance = tile[tile_id]
            try:
                tile_instance.remove_item(uid)
                html = tile_instance()
            except:
                # XXX: Pass silently ?
                pass

        # XXX: Calling the tile will return the HTML with the headers, need to
        #      find out if this affects us in any way.
        return html


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
