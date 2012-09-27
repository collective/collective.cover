# -*- coding: utf-8 -*-

import logging

from zope import schema
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.tiles.interfaces import ITileDataManager

from collective.cover import _
from collective.cover.config import PROJECTNAME
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile

logger = logging.getLogger(PROJECTNAME)


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

    def get_embedding_code():
        """ Returns the embed code stored in the tile.
        """


class EmbedTile(PersistentCoverTile):

    implements(IEmbedTile)

    index = ViewPageTemplateFile('templates/embed.pt')

    is_configurable = True
    is_editable = True

    def get_embedding_code(self):
        return self.data['embed']

    def is_empty(self):
        return not(self.data['embed'] or \
                   self.data['title'] or \
                   self.data['description'])

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()
        logger.debug('tile %s deleted', self.id)

    def accepted_ct(self):
        return None
