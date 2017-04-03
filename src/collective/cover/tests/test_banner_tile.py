# -*- coding: utf-8 -*-
from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.banner import BannerTile
from collective.cover.tiles.banner import IBannerTile
from mock import Mock

import unittest


class BannerTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(BannerTileTestCase, self).setUp()
        self.tile = BannerTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.banner'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IBannerTile
        self.klass = BannerTile
        super(BannerTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ALL_CONTENT_TYPES)

    def test_populate_with_image_object_unicode(self):
        """We must store unicode always on schema.TextLine and schema.Text
        fields to avoid UnicodeDecodeError.
        """
        title = u'El veloz murciélago hindú comía feliz cardillo y kiwi'
        obj = self.portal['my-image']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.data.get('title'), title)
        self.assertIsInstance(self.tile.data.get('title'), unicode)
        self.assertTrue(self.tile.has_image)
        self.assertIsNotNone(self.tile.getRemoteUrl())

    def test_populate_tile_with_image_object_string(self):
        """This test complements test_populate_with_image_object_unicode
        using strings instead of unicode objects.
        """
        title = 'The quick brown fox jumps over the lazy dog'
        obj = self.portal['my-image']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(
            unicode(title, 'utf-8'),
            self.tile.data.get('title')
        )
        self.assertTrue(self.tile.has_image)
        self.assertIsNotNone(self.tile.getRemoteUrl())

    def test_populate_with_link_object_unicode(self):
        """We must store unicode always on schema.TextLine and schema.Text
        fields to avoid UnicodeDecodeError.
        """
        title = u'El veloz murciélago hindú comía feliz cardillo y kiwi'
        obj = self.portal['my-link']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.data.get('title'), title)
        self.assertIsInstance(self.tile.data.get('title'), unicode)
        self.assertFalse(self.tile.has_image)
        self.assertEqual(self.tile.getRemoteUrl(), 'http://plone.org')

    def test_populate_tile_with_link_object_string(self):
        """This test complements test_populate_with_link_object_unicode
        using strings instead of unicode objects.
        """
        title = 'The quick brown fox jumps over the lazy dog'
        obj = self.portal['my-link']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(unicode(title, 'utf-8'), self.tile.data.get('title'))
        self.assertFalse(self.tile.has_image)
        self.assertEqual(self.tile.getRemoteUrl(), 'http://plone.org')

    def test_render_empty(self):
        msg = 'Drag&amp;drop an image or link here to populate the tile.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_render_with_image(self):
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        # the image is there and the alt attribute is set
        self.assertIn('<img ', rendered)
        self.assertIn('alt="This image was created for testing purposes"', rendered)

    def test_render_with_link(self):
        obj = self.portal['my-link']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertNotIn('<img ', rendered)
        self.assertIn('<a href="http://plone.org">Test link</a>', rendered)
