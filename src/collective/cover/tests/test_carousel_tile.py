# -*- coding: utf-8 -*-

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
        self.name = u"collective.cover.carousel"
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
        self.assertFalse(self.tile.is_configurable)
        self.assertTrue(self.tile.is_droppable)
        self.assertTrue(self.tile.is_editable)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())
