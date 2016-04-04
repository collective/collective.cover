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
from zope.interface import implementer


class IContentBodyTile(IPersistentCoverTile):

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


@implementer(IContentBodyTile)
class ContentBodyTile(PersistentCoverTile):

    index = ViewPageTemplateFile('templates/contentbody.pt')

    is_editable = False
    is_configurable = False
    short_name = _(u'msg_short_name_contentbody', default=u'Content Body')

    @property
    def is_empty(self):
        return not self.data.get('uuid', False)

    def body(self):
        """Return the body text of the related object."""
        uuid = self.data.get('uuid', None)
        try:
            obj = uuid and uuidToObject(uuid)
        except Unauthorized:
            return  # TODO: handle exception and show message on template

        if obj is None:
            return ''  # obj was deleted

        try:
            return obj.getText()  # Archetypes
        except AttributeError:
            return obj.text.output if obj.text is not None else ''  # Dexterity

    def populate_with_object(self, obj):
        super(ContentBodyTile, self).populate_with_object(obj)

        data = {
            'uuid': IUUID(obj),
        }

        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    def accepted_ct(self):
        """Return 'Document' and 'News Item' as the only content types
        accepted in the tile.
        """
        return ['Document', 'News Item']

    def item_url(self):
        uuid = self.data.get('uuid', None)
        try:
            obj = uuidToObject(uuid)
        except Unauthorized:
            obj = None

        if obj:
            return obj.absolute_url()
