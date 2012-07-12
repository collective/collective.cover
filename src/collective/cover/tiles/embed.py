# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.tiles.interfaces import ITileDataManager

from collective.composition import _
from collective.composition.tiles.base import IPersistentCompositionTile
from collective.composition.tiles.base import PersistentCompositionTile


class IEmbedTile(IPersistentCompositionTile):

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

    def get_embedding_code():
        """ Returns the embed code stored in the tile.
        """

    def get_title():
        """ Returns the title stored in the tile.
        """

    def get_description():
        """ Returns the description stored in the tile.
        """


class EmbedTile(PersistentCompositionTile):

    implements(IEmbedTile)

    index = ViewPageTemplateFile('templates/embed.pt')

    # TODO: make it configurable
    is_configurable = False

    def get_embedding_code(self):
        return self.data['embed']

    def get_title(self):
        return self.data['title']

    def get_description(self):
        return self.data['description']

    def is_empty(self):
        return not(self.data['embed'] or \
                   self.data['title'] or \
                   self.data['description'])

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = []
        return valid_ct
