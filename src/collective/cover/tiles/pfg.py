# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implementer


class IPFGTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


@implementer(IPFGTile)
class PFGTile(PersistentCoverTile):

    index = ViewPageTemplateFile('templates/pfg.pt')

    is_editable = True
    is_configurable = True
    short_name = _(u'msg_short_name_pfg', default=u'FormGen')

    def body(self):
        body = ''
        uuid = self.data.get('uuid', None)
        try:
            obj = uuid and uuidToObject(uuid)
            if obj is not None:
                body = obj.restrictedTraverse('fg_embedded_view_p3')()
        except Unauthorized:
            body = ''
        return body

    def populate_with_object(self, obj):
        super(PFGTile, self).populate_with_object(obj)

        data = {
            'title': safe_unicode(obj.Title()),
            'description': safe_unicode(obj.Description()),
            'uuid': IUUID(obj),
        }

        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    def accepted_ct(self):
        """Return 'FormFolder' as the only content type accepted in the tile.
        """
        return ['FormFolder']
