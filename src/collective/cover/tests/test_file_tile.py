# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from plone.uuid.interfaces import IUUID

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.file import FileTile
from collective.cover.tiles.base import IPersistentCoverTile


class FileTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.cover = self.portal['frontpage']
        self.tile = self.portal.restrictedTraverse(
            '@@%s/%s' % ('collective.cover.file', 'test-file-tile'))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(FileTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, FileTile))

        tile = FileTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    # FIXME
    @unittest.expectedFailure
    def test_get_title(self):
        self.fail(NotImplemented)

    # FIXME
    @unittest.expectedFailure
    def test_get_description(self):
        self.fail(NotImplemented)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_populate_tile_with_object(self):
        obj = self.portal['my-file']
        self.tile.populate_with_object(obj)

        self.assertEqual(self.tile.data.get('title'), obj.Title())
        self.assertEqual(self.tile.data.get('description'), obj.Description())
        self.assertEqual(self.tile.data.get('uuid'), IUUID(obj))

    def test_populate_tile_with_invalid_object(self):
        obj = self.portal['my-document']
        self.tile.populate_with_object(obj)

        # tile must be still empty
        self.assertTrue(self.tile.is_empty())

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['File'])

    def test_render(self):
        obj = self.portal['my-file']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertTrue('Download file' in rendered)
        self.assertTrue('My file' in rendered)
        self.assertTrue(
            "This file was created for testing purposes" in rendered)

    def test_render_kB_file(self):
        obj = self.portal['my-file']
        obj.setFile('0' * 1024)
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertTrue('1 kB (1024 bytes)' in rendered)
        self.assertTrue('My file' in rendered)
        self.assertTrue(
            "This file was created for testing purposes" in rendered)

    def test_render_MB_file(self):
        obj = self.portal['my-file']
        obj.setFile('0' * 1048576)
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertTrue('1 MB (1048576 bytes)' in rendered)
        self.assertTrue('My file' in rendered)
        self.assertTrue(
            "This file was created for testing purposes" in rendered)
