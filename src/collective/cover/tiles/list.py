# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema
from zope.component import queryUtility
from plone.app.textfield.interfaces import ITransformer

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.namedfile.field import NamedImage

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile


class IListTile(IPersistentCoverTile):

    uuids = schema.List(title=u'Item uuids',
        value_type=schema.TextLine(), readonly=True)

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

    def results():
        """
        This method return a list of the objects in uuids
        """

    def populate_with_object(obj):
        """
        This method will take a CT and will append its uid to uuids
        """

    def delete():
        """
        This method removes the persistent data created for this tile
        """
    def accepted_ct():
        """
        Return a list of supported content types.
        """


class ListTile(PersistentCoverTile):

    index = ViewPageTemplateFile("templates/list.pt")

    is_configurable = False

    def results(self):
        start=0
        size=4
        uuids = self.data.get('uuids', None)
        result = []
        if uuids:
            for uid in uuids:
                obj = uuidToObject(uid)
                result.append(obj)

        return result

    def populate_with_object(self, obj):
        super(ListTile, self).populate_with_object(obj)
        uuid = IUUID(obj, None)
        data_mgr = ITileDataManager(self)
        if data_mgr.get()['uuids']:
            uuids = data_mgr.get()['uuids']
            if uuid not in uuids:
                uuids.append(uuid)
            data_mgr.set({'uuids':uuids})
        else:
            data_mgr.set({'uuids':[uuid]})

    def replace_with_objects(self, objs):
        super(ListTile, self).replace_with_objects(objs)
        data_mgr = ITileDataManager(self)
        data_mgr.set({'uuids':objs})

    def remove_item(self, uid):
        super(ListTile, self).remove_item(uid)
        data_mgr = ITileDataManager(self)
        uids = data_mgr.get()['uuids']
        if uid in uids:
            del uids[uids.index(uid)]
        data_mgr.set({'uuids':uids})

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def get_uid(self, obj):
        return IUUID(obj, None)

    
    def accepted_ct(self):
        return None
    

    
