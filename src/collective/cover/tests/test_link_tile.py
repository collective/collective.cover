# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.link import LinkTile
from collective.cover.tiles.base import IPersistentCoverTile


class LinkTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.portal.restrictedTraverse(
            '@@%s/%s' % ('collective.cover.link', 'test-link-tile'))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(LinkTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, LinkTile))

        tile = LinkTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(),
                         ['Link', ])

    def test_populate_with_object(self):
        self.tile.populate_with_object(self.portal['my-link'])
        self.assertEqual('Test link', self.tile.data['title'])
        self.assertEqual("This link was created for testing purposes",
                         self.tile.data['description'])

    def test_render_empty(self):
        self.assertTrue(
            "Please drag&amp;drop a link here to populate the tile." in self.tile())

    def test_render(self):
        obj = self.portal['my-link']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertTrue('Test link' in rendered)
        self.assertTrue(
            "This link was created for testing purposes" in rendered)
