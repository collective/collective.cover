# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.collection import CollectionTile
from plone.app.imaging.interfaces import IImageScale
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.uuid.interfaces import IUUID
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class CollectionTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.cover = self.portal['frontpage']
        self.tile = CollectionTile(self.cover, self.request)
        # XXX: tile initialization
        self.tile.__name__ = 'collective.cover.collection'

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(CollectionTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, CollectionTile))

        tile = CollectionTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_populate_tile_with_object_unicode(self):
        """We must store unicode always on schema.TextLine and schema.Text
        fields to avoid UnicodeDecodeError.
        """
        title = u'El veloz murciélago hindú comía feliz cardillo y kiwi'
        obj = self.portal['my-collection']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.data.get('header'), title)
        self.assertTrue(self.tile.data.get('footer'))
        self.assertEqual(self.tile.data.get('uuid'), IUUID(obj))
        self.assertIsInstance(self.tile.data.get('header'), unicode)
        self.assertIsInstance(self.tile.data.get('footer'), unicode)

    def test_populate_tile_with_object_string(self):
        """This test complements test_populate_with_object_unicode
        using strings instead of unicode objects.
        """
        title = 'The quick brown fox jumps over the lazy dog'
        obj = self.portal['my-collection']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(
            unicode(title, 'utf-8'),
            self.tile.data.get('header')
        )
        self.assertTrue(self.tile.data.get('footer'))
        self.assertEqual(self.tile.data.get('uuid'), IUUID(obj))

    def test_populate_tile_with_invalid_object(self):
        obj = self.portal['my-document']
        self.tile.populate_with_object(obj)
        self.assertTrue(self.tile.is_empty())

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['Collection'])

    def test_collection_tile_render(self):
        obj = self.portal['my-collection']
        self.tile.populate_with_object(obj)
        rendered = self.tile()

        self.assertIn("<p>The collection doesn't have any results.</p>", rendered)

    def test_delete_collection(self):
        obj = self.portal['my-collection']
        self.tile.populate_with_object(obj)
        self.tile.populate_with_object(obj)
        rendered = self.tile()

        self.assertIn("<p>The collection doesn't have any results.</p>", rendered)

        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Editor', 'Reviewer'])
        login(self.portal, TEST_USER_NAME)
        self.portal.manage_delObjects(['my-collection'])
        rendered = self.tile()

        self.assertIn('Please drop a collection here to fill the tile.', rendered)

    def test_thumbnail(self):
        # as a File does not have an image field, we should have no thumbnail
        obj = self.portal['my-file']
        self.assertFalse(self.tile.thumbnail(obj))

        # as an Image does have an image field, we should have a thumbnail
        obj = self.portal['my-image']
        thumbnail = self.tile.thumbnail(obj)
        self.assertTrue(thumbnail)
        # the thumbnail is an ImageScale
        self.assertTrue(IImageScale.providedBy(thumbnail))

        # turn visibility off, we should have no thumbnail
        # XXX: refactor; we need a method to easily change field visibility
        tile_conf = self.tile.get_tile_configuration()
        tile_conf['image']['visibility'] = u'off'
        self.tile.set_tile_configuration(tile_conf)

        self.assertFalse(self.tile._field_is_visible('image'))
        self.assertFalse(self.tile.thumbnail(obj))

        # TODO: test against Dexterity-based content types

    def test_number_of_items(self):
        collection = self.portal['my-collection']
        image_query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Image',
        }]
        collection.setQuery(image_query)
        collection.setSort_on('id')
        self.tile.populate_with_object(collection)

        # Collection has three images and shows them all.
        self.assertEqual(len(self.tile.results()), 3)

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['number_to_show']['size'] = 2
        self.tile.set_tile_configuration(tile_conf)

        # Collection has three images and shows the first two items.
        items = self.tile.results()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].getId(), 'my-image')
        self.assertEqual(items[1].getId(), 'my-image1')

    def test_offset(self):
        collection = self.portal['my-collection']
        image_query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Image',
        }]
        collection.setQuery(image_query)
        collection.setSort_on('id')
        self.tile.populate_with_object(collection)

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['offset']['offset'] = 1
        self.tile.set_tile_configuration(tile_conf)

        # Collection has three images and shows the final two.
        items = self.tile.results()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].getId(), 'my-image1')
        self.assertEqual(items[1].getId(), 'my-image2')

        # Add a size, so only one item is left.
        tile_conf['number_to_show']['size'] = 1
        self.tile.set_tile_configuration(tile_conf)

        items = self.tile.results()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].getId(), 'my-image1')
