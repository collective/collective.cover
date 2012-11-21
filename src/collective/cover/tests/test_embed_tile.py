# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.embed import EmbedTile
from collective.cover.tiles.base import IPersistentCoverTile


class EmbedTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.cover = self.portal['frontpage']
        self.tile = EmbedTile(self.cover, self.request)

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(EmbedTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, EmbedTile))

        tile = EmbedTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertFalse(self.tile.is_droppable)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_render_empty(self):
        msg = "Please edit the tile to add the code to be embedded."
        self.assertTrue(msg in self.tile())
