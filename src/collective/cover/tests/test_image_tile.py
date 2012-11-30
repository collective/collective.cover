# -*- coding: utf-8 -*-

import unittest2 as unittest
import os

from App.Common import package_home

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.image import ImageTile
from collective.cover.tiles.base import IPersistentCoverTile


def loadImage(name, size=0):
    """Load image from testing directory
    """
    path = os.path.join(package_home(globals()), 'input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data


class ImageTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.portal.restrictedTraverse(
            '@@%s/%s' % ('collective.cover.image', 'test-image-tile'))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(ImageTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, ImageTile))

        tile = ImageTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(),
                         ['Image', ])

    def test_render_empty(self):
        self.assertTrue(
            "Please drag&amp;drop an image here to populate the tile." in self.tile())

    def test_render(self):
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertTrue('test-image-tile/@@images' in rendered)
