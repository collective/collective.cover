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

    def test_populate_tile_with_object(self):
        obj = self.portal['my-collection']
        self.tile.populate_with_object(obj)

        self.assertEqual(self.tile.data.get('uuid'), IUUID(obj))

    def test_populate_tile_with_invalid_object(self):
        obj = self.portal['my-document']
        self.tile.populate_with_object(obj)

        # tile must be still empty
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

        self.assertIn("Please drop a collection here to fill the tile.", rendered)

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
