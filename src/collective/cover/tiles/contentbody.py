# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements


class IContentBodyTile(IPersistentCoverTile):

    uuid = schema.TextLine(title=u'Collection uuid', readonly=True)


class ContentBodyTile(PersistentCoverTile):

    implements(IPersistentCoverTile)

    index = ViewPageTemplateFile('templates/contentbody.pt')

    is_editable = False
    is_configurable = False
    short_name = _(u'msg_short_name_contentbody', default=u'Content Body')

    def body(self):
        body = ''
        uuid = self.data.get('uuid', None)
        try:
            obj = uuid and uuidToObject(uuid)
        except Unauthorized:
            obj = None
        if obj is not None:
            if hasattr(obj, 'getText'):
                body = obj.getText()
            else:
                # Probably Dexterity.
                body = obj.text.output
        return body

    def populate_with_object(self, obj):
        super(ContentBodyTile, self).populate_with_object(obj)

        data = {
            'uuid': IUUID(obj, None),  # XXX: can we get None here? see below
        }

        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    def accepted_ct(self):
        """Return 'Document' and 'News Item' as the only content types
        accepted in the tile.
        """
        return ['Document', 'News Item']
