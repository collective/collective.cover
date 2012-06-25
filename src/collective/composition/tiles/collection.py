# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import TextLine

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.composition.tiles.base import IPersistentCompositionTile
from collective.composition.tiles.base import PersistentCompositionTile


class ICollectionTile(IPersistentCompositionTile):

    uuid = TextLine(title=u'Collection uuid')

    def results():
        """
        This method return a list og
        A method to return the rich text stored in the tile
        """

    def populate_with_object(obj):
        """
        This method will take a CT Collection as parameter, and it will store a
        reference to it.
        """

    def delete():
        """
        This method removes the persistent data created for this tile
        """

    def accepted_ct():
        """
        Return a list of supported content types.
        """

    def has_data():
        """
        A method that return True if the tile have a data.
        """


class CollectionTile(PersistentCompositionTile):

    index = ViewPageTemplateFile("templates/collection.pt")

    is_configurable = True

    def results(self):
        start=0
        size=6
        uuid = self.data.get('uuid', None)
        if uuid is not None:
            obj = uuidToObject(uuid)
            return obj.results(b_start=start, b_size=size)

    def populate_with_object(self, obj):
        uuid = IUUID(obj, None)
        data_mgr = ITileDataManager(self)
        data_mgr.set({'uuid': uuid})

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = ['Collection',]
        return valid_ct

    def has_data(self):
        uuid = self.data.get('uuid', None)
        return uuid is not None
