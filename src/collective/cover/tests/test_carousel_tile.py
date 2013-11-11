# -*- coding: utf-8 -*-

from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.carousel import CarouselTile
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class CarouselTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = u'collective.cover.carousel'
        self.cover = self.portal['frontpage']
        self.tile = getMultiAdapter((self.cover, self.request), name=self.name)
        self.tile = self.tile['test']

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(CarouselTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, CarouselTile))

        tile = CarouselTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_droppable)
        self.assertTrue(self.tile.is_editable)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ALL_CONTENT_TYPES)

    def test_crud(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())

        # now we add a couple of objects to the list
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        self.tile.populate_with_object(obj1)
        self.tile.populate_with_object(obj2)

        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertEqual(len(tile.results()), 2)
        self.assertIn(obj1, tile.results())
        self.assertIn(obj2, tile.results())

        # next, we replace the list of objects with a different one
        obj3 = self.portal['my-news-item']
        tile.replace_with_objects([IUUID(obj3, None)])
        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertNotIn(obj1, tile.results())
        self.assertNotIn(obj2, tile.results())
        self.assertIn(obj3, tile.results())

        # finally, we remove it from the list; the tile must be empty again
        tile.remove_item(obj3.UID())
        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertTrue(tile.is_empty())
