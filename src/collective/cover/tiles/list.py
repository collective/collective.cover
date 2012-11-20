# -*- coding: utf-8 -*-

from zope import schema
from zope.component import queryUtility

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from plone.namedfile.field import NamedImage
from zope.schema import getFieldsInOrder

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile


class IListTile(IPersistentCoverTile):

    uuids = schema.List(title=_(u'Elements'),
        value_type=schema.TextLine(), required=False)

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
        readonly=True
        )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        readonly=True
        )

    image = NamedImage(
        title=_(u'Image'),
        required=False,
        readonly=True
        )


class ListTile(PersistentCoverTile):

    index = ViewPageTemplateFile("templates/list.pt")

    is_configurable = True
    is_editable = False
    limit = 4

    def results(self):
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

    def set_limit(self):
        for field in self.get_configured_fields():
            if field and 'id' in field.keys() and 'size' in field.keys() \
            and field['id'] == 'uuids':
                self.limit = int(field['size'])

    def populate_with_object(self, obj):
        super(ListTile, self).populate_with_object(obj)
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

    def replace_with_objects(self, objs):
        super(ListTile, self).replace_with_objects(objs)
        self.set_limit()
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        if type(objs) == list:
            old_data['uuids'] = objs[:self.limit]
        else:
            old_data['uuids'] = [objs]

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

    def get_uid(self, obj):
        return IUUID(obj, None)

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
