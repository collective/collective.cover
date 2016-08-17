# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from collective.cover.controlpanel import ICoverSettings
from collective.cover.interfaces import IGridSystem
from collective.cover.tiles.list import IListTile
from collective.cover.utils import assign_tile_ids
from collective.cover.vocabularies import TileStylesVocabulary
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.events import EditBegunEvent
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from Products.Five.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.component import queryUtility
from zope.event import notify
from zope.schema.interfaces import IVocabularyFactory

import json


# TODO: implement EditCancelledEvent and EditFinishedEvent
# XXX: we need to leave the view after saving or cancelling editing
class LayoutEdit(BrowserView):

    """Layout Tab."""

    index = ViewPageTemplateFile('templates/layoutedit.pt')

    def setup(self):
        self.context = aq_inner(self.context)
        vocab = TileStylesVocabulary()
        self.css_classes = vocab(self.context)
        # lock the object when someone is editing it
        notify(EditBegunEvent(self.context))

    def can_export_layout(self):
        sm = getSecurityManager()
        portal = api.portal.get()
        # TODO: check permission locally and not in portal context
        return sm.checkPermission('collective.cover: Can Export Layout', portal)

    def layoutmanager_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        grid = getUtility(IGridSystem, name=settings.grid_system)
        return json.dumps({'ncolumns': grid.ncolumns})

    def render(self):
        if 'export-layout' in self.request and self.can_export_layout():
            name = self.request.get('layout-name', None)
            if name:
                layout = self.context.cover_layout

                registry = getUtility(IRegistry)
                settings = registry.forInterface(ICoverSettings)

                # Store name and layout as unicode.  Note that the
                # name must only contain ascii because it is used as
                # value for a vocabulary.
                name = name.decode('ascii', 'ignore')
                layout = layout.decode('utf-8')
                settings.layouts[name] = layout

        return self.index()

    def __call__(self):
        self.setup()
        return self.render()


class PageLayout(BrowserView):

    """Renders a layout for the cover object."""

    pagelayout = ViewPageTemplateFile('templates/pagelayout.pt')
    row = ViewPageTemplateFile('templates/row.pt')
    group = ViewPageTemplateFile('templates/group.pt')
    tile = ViewPageTemplateFile('templates/tile.pt')
    generalmarkup = ViewPageTemplateFile('templates/generalmarkup.pt')

    def get_layout(self, mode):
        layout = json.loads(self.context.cover_layout)

        if mode == 'compose' or mode == 'layout_edit':
            self.grid_layout_common(layout)

        if mode == 'view' or mode == 'compose':
            registry = getUtility(IRegistry)
            settings = registry.forInterface(ICoverSettings)
            grid = getUtility(IGridSystem, name=settings.grid_system)

            grid.transform(layout)
        else:
            self.grid_layout_edit(layout)

        return layout

    def grid_layout_common(self, layout):
        """Add things to the grid/layout structure which should be
        available on both compose and layout tabs.
        """

        for element in layout:
            if 'type' in element:
                if element['type'] == 'tile':
                    tile_type = getUtility(ITileType, element['tile-type'])
                    element['tile-title'] = tile_type.title

                if 'children' in element:
                    self.grid_layout_common(element['children'])

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
        if 'type' not in section:
            return self.generalmarkup(section=section, mode=mode)

        if section['type'] == u'row':
            return self.row(section=section, mode=mode)
        elif section['type'] == u'group':
            return self.group(section=section, mode=mode)
        elif section['type'] == u'tile':
            tile_url = '@@{0}/{1}'.format(section.get('tile-type'),
                                          section.get('id'))
            tile = self.context.restrictedTraverse(tile_url.encode(), None)
            if tile is None:
                return '<div class="tileNotFound">Could not find tile</div>'
            if mode == 'layout_edit':
                css_class = 'cover-tile '
            else:
                css_class = 'tile '
            tile_conf = tile.get_tile_configuration()
            css_class += tile_conf.get('css_class', '')
            section['css_class'] = css_class.strip()
            return self.tile(section=section, mode=mode, tile_url=tile_url)

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
        tile = self.context.restrictedTraverse('{0}/{1}'.format(str(tile_type), str(tile_id)))
        if not tile.isAllowedToEdit():
            return u'disabled'
        else:
            return u''

    def render_view(self):
        # XXX: There *must* be a better way of doing this, maybe write it
        #      in the request ? sending it as parameter is way too ugly
        return self.pagelayout(mode='view')

    def render_compose(self):
        # XXX: There *must* be a better way of doing this, maybe write it
        #      in the request ? sending it as parameter is way too ugly
        return self.pagelayout(mode='compose')

    def render_layout_edit(self):
        # XXX: There *must* be a better way of doing this, maybe write it
        #      in the request ? sending it as parameter is way too ugly
        return self.pagelayout(mode='layout_edit')

    def accepted_ct_for_tile(self, tile_type):
        tile = self.context.restrictedTraverse(str(tile_type))
        accepted_ct = tile.accepted_ct()

        return json.dumps(accepted_ct)

    def get_content_portal_type(self, tile_type, tile_id):
        """Return content type of data inside the tile."""
        tile = self.context.restrictedTraverse('{0}/{1}'.format(str(tile_type), str(tile_id)))
        data_mgr = ITileDataManager(tile)
        data = data_mgr.get()
        uuid = data.get('uuid', None)
        if uuid is None:
            return
        obj = uuidToObject(uuid)
        if obj is None:
            return
        return obj.portal_type

    def get_content_uuid(self, tile_type, tile_id):
        """Return UUID of data inside the tile."""
        tile = self.context.restrictedTraverse('{0}/{1}'.format(str(tile_type), str(tile_id)))
        data_mgr = ITileDataManager(tile)
        data = data_mgr.get()
        return data.get('uuid', None)

    def get_has_subitem(self, tile_type, tile_id):
        """Return if tile has subitems (inherited from IListTile)."""
        tile = self.context.restrictedTraverse('{0}/{1}'.format(str(tile_type), str(tile_id)))
        return IListTile.providedBy(tile)

    def __call__(self):
        return self.render_view()


class LayoutSave(BrowserView):

    """Helper browser view to save the layout of a tile."""

    def setup(self):
        self.cover_layout = self.request.get('cover_layout')

    def __call__(self):
        self.setup()

        layout = json.loads(self.cover_layout)

        assign_tile_ids(layout, override=False)

        self.cover_layout = json.dumps(layout)

        self.context.cover_layout = self.cover_layout
        self.context.reindexObject()

        return 'saved'


class TileList(BrowserView):

    """Helper browser view to create a list of tiles."""

    index = ViewPageTemplateFile('templates/tilelist.pt')

    def setup(self):
        self.context = aq_inner(self.context)
        vocab_name = 'collective.cover.AvailableTiles'
        available_tiles = queryUtility(IVocabularyFactory, vocab_name)
        # the view is expecting a dictionary of "tile types"
        self.tiles = [{'tile_type': name.value}
                      for name in available_tiles(self.context)]

    def get_tile_metadata(self, tile_name):
        tile_type = getUtility(ITileType, tile_name)
        tile = self.context.restrictedTraverse(str(tile_name))
        title = tile.short_name
        if not title:
            title = tile_type.title
        tile_metadata = {
            'icon': tile_type.icon,
            'description': tile_type.description,
            'title': title,
            'is_configurable': tile.is_configurable and 1 or 0
        }

        return tile_metadata

    def __call__(self):
        self.setup()
        return self.index()


class GroupSelect(BrowserView):

    """Helper browser view to create a list of groups to manage the tile."""

    index = ViewPageTemplateFile('templates/groupselect.pt')

    def setup(self):
        vocab_name = 'plone.app.vocabularies.Groups'
        groups_factory = queryUtility(IVocabularyFactory, vocab_name)
        self.groups = groups_factory(self.context)
        if 'groups[]' in self.request.keys():
            groups = self.request['groups[]']
            tile_len = int(self.request['tile_len'])
            i = 0
            while(i < tile_len):
                tile_type = self.request['tiles[{0}][type]'.format(i)]
                tile_id = self.request['tiles[{0}][id]'.format(i)]
                tile = self.context.restrictedTraverse('{0}/{1}'.format(tile_type, tile_id))
                tile.setAllowedGroupsForEdit(groups)
                i += 1

    def __call__(self):
        self.setup()
        return self.index()
