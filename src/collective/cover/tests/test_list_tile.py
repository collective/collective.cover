# -*- coding: utf-8 -*-

from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.list import ListTile
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class ListTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = u'collective.cover.list'
        self.cover = self.portal['frontpage']
        self.tile = getMultiAdapter((self.cover, self.request), name=self.name)
        self.tile = self.tile['test']

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(ListTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, ListTile))

        tile = ListTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_droppable)
        self.assertFalse(self.tile.is_editable)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_crud(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())

        # now we add a couple of objects to the list
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        self.tile.populate_with_object(obj1)
        self.tile.populate_with_object(obj2)

        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertEqual(len(tile.results()), 2)
        self.assertIn(obj1, tile.results())
        self.assertIn(obj2, tile.results())

        # next, we replace the list of objects with a different one
        obj3 = self.portal['my-news-item']
        tile.replace_with_objects([IUUID(obj3, None)])
        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertNotIn(obj1, tile.results())
        self.assertNotIn(obj2, tile.results())
        self.assertIn(obj3, tile.results())

        # finally, we remove it from the list; the tile must be empty again
        tile.remove_item(obj3.UID())
        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertTrue(tile.is_empty())

    def test_populate_with_uids(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())

        # now we add a couple of objects to the list
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        self.tile.populate_with_uids([IUUID(obj1, None), IUUID(obj2, None)])

        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertEqual(len(tile.results()), 2)
        self.assertIn(obj1, tile.results())
        self.assertIn(obj2, tile.results())

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ALL_CONTENT_TYPES)

    def test_render_empty(self):
        msg = 'Please add up to 5 objects to the tile.'
        self.assertIn(msg, self.tile())

    def test_remove_item_from_list_tile(self):
        # now we add a couple of objects to the list
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        self.tile.populate_with_object(obj1)
        self.tile.populate_with_object(obj2)

        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']

        self.request.form['tile-type'] = 'collective.cover.list'
        self.request.form['tile-id'] = 'test'
        self.request.form['uid'] = obj1.UID()
        view = getMultiAdapter(
            (self.cover, self.request), name='removeitemfromlisttile')
        self.assertIn(obj1, tile.results())
        view.render()
        self.assertNotIn(obj1, tile.results())

    def test_get_image_position(self):
        # we use the private method to skip memoize cache
        self.assertEqual(self.tile._get_image_position(), u'left')
        tile_conf = self.tile.get_tile_configuration()
        tile_conf['image']['position'] = u'right'
        self.tile.set_tile_configuration(tile_conf)
        self.assertEqual(self.tile._get_image_position(), u'right')

    def test_get_title_tag(self):
        # we use the private method to skip memoize cache
        item = self.portal['my-news-item']
        expected = '<h2><a href="http://nohost/plone/my-news-item">Test news item</a></h2>'
        self.assertEqual(self.tile._get_title_tag(item), expected)
        tile_conf = self.tile.get_tile_configuration()
        tile_conf['title']['htmltag'] = u'h1'
        self.tile.set_tile_configuration(tile_conf)
        expected = '<h1><a href="http://nohost/plone/my-news-item">Test news item</a></h1>'
        self.assertEqual(self.tile._get_title_tag(item), expected)
