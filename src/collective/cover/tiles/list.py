# -*- coding: utf-8 -*-

from zope import schema
from zope.component import queryUtility
from zope.component import getUtility
from zope.interface import implements
from zope.schema import getFieldsInOrder

from plone.registry.interfaces import IRegistry
from plone.app.uuid.utils import uuidToObject
from plone.namedfile.field import NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from plone.uuid.interfaces import IUUID
from plone.memoize import view

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.controlpanel import ICoverSettings


# XXX: we must refactor this tile
class IListTile(IPersistentCoverTile):

    uuids = schema.List(
        title=_(u'Elements'),
        value_type=schema.TextLine(),
        required=False,
    )

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
        readonly=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        readonly=True,
    )

    image = NamedImage(
        title=_(u'Image'),
        required=False,
        readonly=True,
    )


class ListTile(PersistentCoverTile):

    implements(IListTile)

    index = ViewPageTemplateFile("templates/list.pt")

    is_configurable = True
    is_droppable = True
    is_editable = False
    limit = 5

    def results(self):
        """ Return the list of objects stored in the tile.
        """
        self.set_limit()
        uuids = self.data.get('uuids', None)
        result = []
        if uuids:
            uuids = [uuids] if type(uuids) == str else uuids
            for uid in uuids:
                obj = uuidToObject(uid)
                if obj:
                    result.append(obj)
                else:
                    self.remove_item(uid)
        return result[:self.limit]

    def is_empty(self):
        return self.results() == []

    # XXX: we could get rid of this fixing the tile's schema
    def set_limit(self):
        for field in self.get_configured_fields():
            if field and field.get('id') == 'uuids':
                self.limit = int(field.get('size', self.limit))

    def populate_with_object(self, obj):
        super(ListTile, self).populate_with_object(obj)  # check permission
        self.set_limit()
        uuid = IUUID(obj, None)
        data_mgr = ITileDataManager(self)

        old_data = data_mgr.get()
        if data_mgr.get()['uuids']:
            uuids = data_mgr.get()['uuids']
            if type(uuids) != list:
                uuids = [uuid]
            elif uuid not in uuids:
                uuids.append(uuid)

            old_data['uuids'] = uuids[:self.limit]
        else:
            old_data['uuids'] = [uuid]
        data_mgr.set(old_data)

    def replace_with_objects(self, uids):
        super(ListTile, self).replace_with_objects(uids)  # check permission
        self.set_limit()
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        if type(uids) == list:
            old_data['uuids'] = [i for i in uids][:self.limit]
        else:
            old_data['uuids'] = [uids]

        data_mgr.set(old_data)

    def remove_item(self, uid):
        super(ListTile, self).remove_item(uid)
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        uids = data_mgr.get()['uuids']
        if uid in uids:
            del uids[uids.index(uid)]
        old_data['uuids'] = uids
        data_mgr.set(old_data)

    # XXX: are we using this function somewhere? remove?
    def get_uid(self, obj):
        return IUUID(obj, None)

    # XXX: refactoring the tile's schema should be a way to avoid this
    def get_configured_fields(self):
        # Override this method, since we are not storing anything
        # in the fields, we just use them for configuration
        tileType = queryUtility(ITileType, name=self.__name__)
        conf = self.get_tile_configuration()

        fields = getFieldsInOrder(tileType.schema)

        results = []
        for name, obj in fields:
            field = {'id': name,
                     'title': obj.title}
            if name in conf:
                field_conf = conf[name]
                if ('visibility' in field_conf and field_conf['visibility'] == u'off'):
                    # If the field was configured to be invisible, then just
                    # ignore it
                    continue

                if 'htmltag' in field_conf:
                    # If this field has the capability to change its html tag
                    # render, save it here
                    field['htmltag'] = field_conf['htmltag']

                if 'imgsize' in field_conf:
                    field['scale'] = field_conf['imgsize']

                if 'size' in field_conf:
                    field['size'] = field_conf['size']

            results.append(field)

        return results

    @view.memoize
    def accepted_ct(self):
        """
            Return a list with accepted content types ids
            basic tile accepts every content type
            allowed by the cover control panel

            this method is called for every tile in the compose view
            please memoize if you're doing some very expensive calculation
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        return settings.searchable_content_types
