# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements

from plone.app.uuid.utils import uuidToObject


from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile


class IContentBodyTile(IPersistentCoverTile):

    uuid = schema.TextLine(title=u'Collection uuid', readonly=True)


class ContentBodyTile(PersistentCoverTile):

    implements(IPersistentCoverTile)

    index = ViewPageTemplateFile("templates/contentbody.pt")

    is_editable = False
    is_configurable = False

    def body(self):
        body = ''
        uuid = self.data.get('uuid', None)
        if uuid is not None:
            obj = uuidToObject(uuid)
            body = obj.getText()
        return body

    def populate_with_object(self, obj):
        super(ContentBodyTile, self).populate_with_object(obj)

        data = {
            'uuid': IUUID(obj, None),  # XXX: can we get None here? see below
        }

        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    def accepted_ct(self):
        """ For now we are supporting Document and News Item
        """
        return ['Document', 'News Item']
