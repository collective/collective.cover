# -*- coding: utf-8 -*-
from collective.cover.tests.base import TestTileMixin
from collective.cover.tests.utils import set_file_field
from collective.cover.tiles.file import FileTile
from collective.cover.tiles.file import IFileTile
from plone import api
from plone.uuid.interfaces import IUUID

import unittest


class FileTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(FileTileTestCase, self).setUp()
        self.tile = FileTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.file'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IFileTile
        self.klass = FileTile
        super(FileTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['File'])

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

    def test_render(self):
        obj = self.portal['my-file']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('Download file', rendered)
        self.assertIn('My file', rendered)
        self.assertIn('This file was created for testing purposes', rendered)

    def test_remove_file(self):
        # https://github.com/collective/collective.cover/issues/588
        obj = self.portal['my-file']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn(
            '<a href="http://nohost/plone/my-file/at_download/file">', rendered)
        self.assertIn('Download file', rendered)
        api.content.delete(obj)
        rendered = self.tile()
        self.assertNotIn(
            '<a href="http://nohost/plone/my-file/at_download/file">', rendered)
        self.assertNotIn('Download file', rendered)

    def test_render_kB_file(self):
        obj = self.portal['my-file']
        set_file_field(obj, '0' * 1024)  # handle Archetypes and Dexterity
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('1 kB (1024 bytes)', rendered)
        self.assertIn('My file', rendered)
        self.assertIn('This file was created for testing purposes', rendered)

    def test_render_MB_file(self):
        obj = self.portal['my-file']
        set_file_field(obj, '0' * 1048576)  # handle Archetypes and Dexterity
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('1 MB (1048576 bytes)', rendered)
        self.assertIn('My file', rendered)
        self.assertIn('This file was created for testing purposes', rendered)
