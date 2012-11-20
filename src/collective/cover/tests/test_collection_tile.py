# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from plone.uuid.interfaces import IUUID

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.collection import CollectionTile
from collective.cover.tiles.base import IPersistentCoverTile


class CollectionTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.cover = self.portal['frontpage']
        self.tile = CollectionTile(self.cover, self.request)

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(CollectionTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, CollectionTile))

        tile = CollectionTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertFalse(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_populate_tile_with_object(self):
        obj = self.portal['my-collection']
        self.tile.populate_with_object(obj)

        self.assertEqual(self.tile.data.get('uuid'), IUUID(obj))

    def test_populate_tile_with_invalid_object(self):
        obj = self.portal['my-document']
        self.tile.populate_with_object(obj)

        # tile must be still empty
        self.assertTrue(self.tile.is_empty())

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['Collection'])
