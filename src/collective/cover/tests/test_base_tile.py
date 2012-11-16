# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from plone.tiles.interfaces import IPersistentTile

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.base import IPersistentCoverTile


class BaseTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
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

    def test_no_content_type_accepted_by_default(self):
        self.assertEqual(self.tile.accepted_ct(), None)

    def test_delete_tile(self):
        self.tile.delete()
        # TODO: test that ObjectModifiedEvent was fired for the cover
        self.fail(NotImplemented)
