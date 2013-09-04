# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.image import ImageTile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class ImageTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.portal.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.image', 'test-image-tile'))

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
        self.assertEqual(self.tile.accepted_ct(), ['Image'])

    def test_render_empty(self):
        self.assertIn(
            "Drag&amp;drop an image here to populate the tile.", self.tile())

    def test_render(self):
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('src="http://nohost/plone/my-image/@@images', rendered)

    def test_render_deleted_object(self):
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        # delete original object
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.manage_delObjects(['my-image'])
        rendered = self.tile()
        # no image is rendered
        self.assertNotIn('src="http://nohost/plone/my-image/@@images', rendered)

    @unittest.expectedFailure
    def test_alt_atribute_present_in_image(self):
        """Object's title must be displayed in image alt attribute.
        See: https://github.com/collective/collective.cover/issues/182
        """
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('alt="Test image"', rendered)

    def test_change_images(self):
        obj = self.portal['my-image']
        obj1 = self.portal['my-image1']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        # the tile renders the image
        self.assertIn('src="http://nohost/plone/my-image/@@images', rendered)
        # instantiate the tile again
        self.tile = self.portal.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.image', 'test-image-tile'))
        self.tile.populate_with_object(obj1)
        rendered = self.tile()
        # the tile renders the new image
        self.assertIn('src="http://nohost/plone/my-image1/@@images', rendered)
