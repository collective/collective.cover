# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.richtext import RichTextTile
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class RichTextTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.portal.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.richtext', 'test-richtext-tile'))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(RichTextTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, RichTextTile))

        tile = RichTextTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['Document'])

    def test_populate_with_object(self):
        self.tile.populate_with_object(self.portal['my-document'])
        self.assertEqual(self.tile.getText(), '')

    def test_render_empty(self):
        self.assertIn('Please edit the tile to enter some text.', self.tile())

    def test_render(self):
        obj = self.portal['my-document']
        obj.setText('<p>My document text...</p>')
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('<p>My document text...</p>', rendered)
