# -*- coding: utf-8 -*-

# Basic implementation taken from
# http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts

from zope.component import getMultiAdapter

from zope.interface import implements
from zope.interface import Interface

from plone import tiles
from plone.tiles.interfaces import ITileDataManager

from collective.composition.tiles.configuration import ITilesConfigurationScreen


class IPersistentCompositionTile(Interface):
    """
    Base interface for tiles that go into the composition object
    """

    def populate_with_object(obj):
        """
        This method will take a CT object as parameter, and it will store the
        content into the tile. Each tile should implement its own method.
        """

    def delete():
        """
        This method removes the persistent data created for this tile
        """

    def accepted_ct():
        """
        This method returns a list of valid CT that this tile will accept, or
        None if not
        """

    def get_tile_configuration():
        """
        A method that will return the configuration options for this tile
        """


class PersistentCompositionTile(tiles.PersistentTile):

    implements(IPersistentCompositionTile)

    is_configurable = False

    def populate_with_object(self, obj):
        raise NotImplemented

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = None
        return valid_ct

    def get_tile_configuration(self):
        tile_conf_adapter = getMultiAdapter((self.context, self.request, self),
                                             ITilesConfigurationScreen)

        configuration = tile_conf_adapter.get_configuration()

        return configuration