# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.file import FileTile
from plone.uuid.interfaces import IUUID
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class FileTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.cover = self.portal['frontpage']
        self.tile = self.portal.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.file', 'test-file-tile'))

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

    def test_populate_tile_with_object_unicode(self):
        """We must store unicode always on schema.TextLine and schema.Text
        fields to avoid UnicodeDecodeError.
        """
        title = u'παν γράμμα'
        description = u'El veloz murciélago hindú comía feliz cardillo y kiwi'
        obj = self.portal['my-file']
        obj.setTitle(title)
        obj.setDescription(description)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.data.get('title'), title)
        self.assertEqual(self.tile.data.get('description'), description)
        self.assertEqual(self.tile.data.get('uuid'), IUUID(obj))
        self.assertIsInstance(self.tile.data.get('title'), unicode)
        self.assertIsInstance(self.tile.data.get('description'), unicode)

    def test_populate_tile_with_object_string(self):
        """This test complements test_populate_with_object_unicode
        using strings instead of unicode objects.
        """
        title = 'Pangram'
        description = 'The quick brown fox jumps over the lazy dog'
        obj = self.portal['my-file']
        obj.setTitle(title)
        obj.setDescription(description)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(
            unicode(title, 'utf-8'),
            self.tile.data.get('title')
        )
        self.assertEqual(
            unicode(description, 'utf-8'),
            self.tile.data.get('description')
        )
        self.assertEqual(self.tile.data.get('uuid'), IUUID(obj))

    def test_populate_tile_with_invalid_object(self):
        obj = self.portal['my-document']
        self.tile.populate_with_object(obj)
        self.assertTrue(self.tile.is_empty())

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['File'])

    def test_render(self):
        obj = self.portal['my-file']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('Download file', rendered)
        self.assertIn('My file', rendered)
        self.assertIn('This file was created for testing purposes', rendered)

    def test_render_kB_file(self):
        obj = self.portal['my-file']
        obj.setFile('0' * 1024)
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('1 kB (1024 bytes)', rendered)
        self.assertIn('My file', rendered)
        self.assertIn('This file was created for testing purposes', rendered)

    def test_render_MB_file(self):
        obj = self.portal['my-file']
        obj.setFile('0' * 1048576)
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('1 MB (1048576 bytes)', rendered)
        self.assertIn('My file', rendered)
        self.assertIn('This file was created for testing purposes', rendered)
