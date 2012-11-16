# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.file import FileTile
from collective.cover.tiles.base import IPersistentCoverTile


class FileTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('collective.cover.content', 'cover')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.cover = self.portal['cover']
        self.tile = FileTile(self.cover, self.request)

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

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['File'])
