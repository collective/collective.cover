# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile


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

    def get_embedding_code(self):
        return self.data['embed']

    def is_empty(self):
        return not(self.data.get('embed') or
                   self.data.get('title') or
                   self.data.get('description'))
