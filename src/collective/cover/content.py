# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from collective.cover.controlpanel import ICoverSettings
from collective.cover.utils import assign_tile_ids
from five import grok
from plone.dexterity.content import Item
from plone.dexterity.events import EditBegunEvent
from plone.directives import form
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import IDAVAware
from zope.component import getUtility
from zope.container.interfaces import IObjectAddedEvent
from zope.event import notify
from zope.interface import implements

import json

grok.templatedir('templates')


class ICover(form.Schema):
    """
    Composable page
    """
    form.model("models/cover.xml")


class Cover(Item):
    """
    """
    # XXX: Provide this so Cover items can be imported using the import
    #      content from GS, until a proper solution is found.
    #      ref: http://thread.gmane.org/gmane.comp.web.zope.plone.devel/31799
    implements(IDAVAware)


# TODO: move browser views to browser folder
class View(grok.View):
    grok.context(ICover)
    grok.require('zope2.View')
    grok.name('view')


class Standard(grok.View):
    grok.context(ICover)
    grok.require('zope2.View')
    grok.name('standard')


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
        if 'export-layout' in self.request and self.can_export_layout():
            name = self.request.get('layout-name', None)
            if name:
                layout = self.context.cover_layout

                registry = getUtility(IRegistry)

                settings = registry.forInterface(ICoverSettings)

                settings.layouts[name] = unicode(layout)

        return super(LayoutEdit, self).__call__()

    def can_export_layout(self):
        sm = getSecurityManager()
        portal = getToolByName(self.context, "portal_url").getPortalObject()
        # TODO: check permission locally and not in portal context
        return sm.checkPermission('collective.cover: Can Export Layout', portal)


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
