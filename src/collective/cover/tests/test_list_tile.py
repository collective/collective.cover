# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.list import ListTile
from collective.cover.tiles.base import IPersistentCoverTile


class ListTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        name = u"collective.cover.list"
        self.cover = self.portal['frontpage']
        self.tile = getMultiAdapter((self.cover, self.request), name=name)
        self.tile = self.tile['test']

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(ListTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, ListTile))

        tile = ListTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertFalse(self.tile.is_droppable)
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
        self.assertEqual(len(self.tile.results()), 2)
        self.assertTrue(obj1 in self.tile.results())
        self.assertTrue(obj2 in self.tile.results())

        # next, we replace the list of objects with a different one
        obj3 = self.portal['my-news-item']
        self.tile.replace_with_objects([obj3])
        self.assertTrue(obj1 not in self.tile.results())
        self.assertTrue(obj2 not in self.tile.results())
        self.assertTrue(obj3 in self.tile.results())

        # finally, we remove it from the list; the tile must be empty again
        self.tile.remove_item(obj3)
        self.assertTrue(self.tile.is_empty())

    def test_accepted_content_types(self):
        # all content types are accepted
        # XXX: return None don't work
        #self.assertEqual(self.tile.accepted_ct(), None)
        self.assertEqual(self.tile.accepted_ct(),
                         ['Collection', 'Document', 'File',
                          'Image', 'Link', 'News Item'])

    def test_render_empty(self):
        msg = "Please add up to 5 objects to the tile."
        self.assertTrue(msg in self.tile())
