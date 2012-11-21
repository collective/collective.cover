# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.basic import BasicTile
from collective.cover.tiles.base import IPersistentCoverTile


class BasicTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = BasicTile(self.portal, self.request)

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(BasicTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, BasicTile))

        tile = BasicTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(),
                         ['Collection', 'Document', 'File',
                          'Image', 'Link', 'News Item'])
