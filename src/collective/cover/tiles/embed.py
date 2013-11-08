# -*- coding: utf-8 -*-

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements


class IEmbedTile(IPersistentCoverTile):

    embed = schema.Text(
        title=_(u'Embedding code'),
        required=False,
    )

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )


class EmbedTile(PersistentCoverTile):

    implements(IEmbedTile)
    index = ViewPageTemplateFile('templates/embed.pt')

    is_configurable = True
    is_editable = True
    is_droppable = False
    short_name = _(u'msg_short_name_embed', default=u'Embed')

    def is_empty(self):
        return not (self.data.get('embed', None) or
                    self.data.get('title', None) or
                    self.data.get('description', None))

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []
