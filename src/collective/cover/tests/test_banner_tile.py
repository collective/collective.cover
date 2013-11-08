# -*- coding: utf-8 -*-

from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.banner import BannerTile
from collective.cover.tiles.base import IPersistentCoverTile
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileType
from zope.component import getUtility
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class BannerTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = 'collective.cover.banner'
        self.tile = self.portal.restrictedTraverse(
            '@@{0}/{1}'.format(self.name, 'test-tile'))

    @unittest.expectedFailure
    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(BannerTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, BannerTile))

        tile = BannerTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        # FIXME: @property decorator on class methods makes this test fail
        #        how can we fix it?
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_tile_registration(self):
        tile_type = getUtility(ITileType, self.name)
        self.assertIsNotNone(tile_type)
        self.assertTrue(issubclass(tile_type.schema, IPersistentCoverTile))
        registry = getUtility(IRegistry)
        self.assertIn(self.name, registry['plone.app.tiles'])

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
        remote_url = 'http://plone.org'
        obj = self.portal['my-link']
        obj.setTitle(title)
        obj.setRemoteUrl('http://plone.org')
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.data.get('title'), title)
        self.assertIsInstance(self.tile.data.get('title'), unicode)
        self.assertFalse(self.tile.has_image)
        self.assertEqual(self.tile.getRemoteUrl(), remote_url)

    def test_populate_tile_with_link_object_string(self):
        """This test complements test_populate_with_link_object_unicode
        using strings instead of unicode objects.
        """
        title = 'The quick brown fox jumps over the lazy dog'
        remote_url = 'http://plone.org'
        obj = self.portal['my-link']
        obj.setTitle(title)
        obj.setRemoteUrl('http://plone.org')
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(
            unicode(title, 'utf-8'),
            self.tile.data.get('title')
        )
        self.assertFalse(self.tile.has_image)
        self.assertEqual(self.tile.getRemoteUrl(), remote_url)

    def test_render_empty(self):
        self.assertIn(
            'Drag&amp;drop an image or link here to populate the tile.', self.tile())

    def test_render_with_image(self):
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('<img ', rendered)
        # https://github.com/collective/collective.cover/issues/182
        self.assertIn('alt="Test image"', rendered)

    def test_render_with_link(self):
        obj = self.portal['my-link']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertNotIn('<img ', rendered)
        # FIXME: set remote_url on the object
        self.assertIn('<a href="http://">Test link</a>', rendered)
