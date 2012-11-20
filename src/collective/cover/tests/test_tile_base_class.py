# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import eventtesting

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from plone.tiles.interfaces import IPersistentTile
from plone.tiles.interfaces import ITileDataManager

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.base import IPersistentCoverTile


class BaseTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        eventtesting.setUp()

        self.tile = PersistentCoverTile(self.portal, self.request)

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(PersistentCoverTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, PersistentCoverTile))
        # cover tiles inherit from plone.tile PersistentTile
        self.assertTrue(IPersistentTile.implementedBy(PersistentCoverTile))

        tile = PersistentCoverTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))
        # cover tiles inherit from plone.tile PersistentTile
        self.assertTrue(IPersistentTile.providedBy(tile))
        #self.assertTrue(verifyObject(IPersistentTile, tile))

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_all_content_types_accepted_by_default(self):
        self.assertEqual(self.tile.accepted_ct(), None)

    def test_delete_tile_persistent_data(self):
        eventtesting.clearEvents()
        # First, let's assign an id to the tile and store some data
        self.tile.id = 'test-tile'
        data_mgr = ITileDataManager(self.tile)
        data_mgr.set({'test': 'data'})

        # We see that the data persists
        self.assertEqual(data_mgr.get(), {'test': 'data'})

        # Call the delete method
        self.tile.delete()

        # Now we should not see the stored data anymore
        self.assertEqual(data_mgr.get(), {})

        events = eventtesting.getEvents()

        # Finally, test that ObjectModifiedEvent was fired for the cover
        self.assertEqual(events[0].object, self.portal)
