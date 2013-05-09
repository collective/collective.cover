# -*- coding: utf-8 -*-

from collective.cover.testing import generate_jpeg
from collective.cover.testing import images_are_equal
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.image import ImageTile
from PIL import Image
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
        self.assertIn('test-image-tile/@@images', rendered)

    def test_render_deleted_object(self):
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        # Delete original object
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.manage_delObjects(['my-image', ])

        rendered = self.tile()
        # We keep a copy of the image data here
        self.assertIn('test-image-tile/@@images', rendered)

    @unittest.expectedFailure
    def test_alt_atribute_present_in_image(self):
        """Object's title must be displayed in image alt attribute.
        See: https://github.com/collective/collective.cover/issues/182
        """
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('alt="Test image"', rendered)

    def test_image_traverser(self):
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        scales = self.layer['portal'].restrictedTraverse('@@%s/%s/@@images' %
                                                         ('collective.cover.image',
                                                          'test-image-tile',))
        img = scales.scale('image')
        self.assertTrue(images_are_equal(str(self.tile.data['image'].data),
                                         str(img.index_html().read())))

    def test_change_images(self):
        obj = self.portal['my-image']
        obj1 = self.portal['my-image1']
        obj2 = self.portal['my-image2']

        tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                       ('collective.cover.image',
                                                        'test-image-tile',))
        tile.populate_with_object(obj1)
        rendered = tile()
        self.assertTrue('test-image-tile/@@images' in rendered)
        self.assertTrue(images_are_equal(str(tile.data['image'].data),
                                         str(obj1.getImage())))
        scales = self.layer['portal'].restrictedTraverse('@@%s/%s/@@images' %
                                                         ('collective.cover.image',
                                                          'test-image-tile',))
        img = scales.scale('image')
        self.assertTrue(images_are_equal(str(tile.data['image'].data),
                                         str(img.index_html().read())))
        self.assertTrue(images_are_equal(str(img.index_html().read()),
                                         str(obj1.getImage())))

        tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                       ('collective.cover.image',
                                                        'test-image-tile',))
        tile.populate_with_object(obj)
        rendered = tile()
        self.assertTrue('test-image-tile/@@images' in rendered)
        self.assertFalse(images_are_equal(str(tile.data['image'].data),
                                          str(obj1.getImage())))
        self.assertTrue(images_are_equal(str(tile.data['image'].data),
                                         str(obj.getImage())))
        scales = self.layer['portal'].restrictedTraverse('@@%s/%s/@@images' %
                                                         ('collective.cover.image',
                                                          'test-image-tile',))
        img = scales.scale('image')
        self.assertTrue(images_are_equal(str(tile.data['image'].data),
                                         str(img.index_html().read())))
        self.assertTrue(images_are_equal(str(img.index_html().read()),
                                         str(obj.getImage())))

        tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                       ('collective.cover.image',
                                                        'test-image-tile',))
        tile.populate_with_object(obj2)
        rendered = tile()
        self.assertTrue('test-image-tile/@@images' in rendered)
        self.assertFalse(images_are_equal(str(tile.data['image'].data),
                                          str(obj1.getImage())))
        self.assertFalse(images_are_equal(str(tile.data['image'].data),
                                          str(obj.getImage())))
        self.assertTrue(images_are_equal(str(tile.data['image'].data),
                                         str(obj2.getImage())))
        scales = self.layer['portal'].restrictedTraverse('@@%s/%s/@@images' %
                                                         ('collective.cover.image',
                                                          'test-image-tile',))
        img = scales.scale('image')
        self.assertTrue(images_are_equal(str(tile.data['image'].data),
                                         str(img.index_html().read())))
        self.assertTrue(images_are_equal(str(img.index_html().read()),
                                         str(obj2.getImage())))

    def test_change_images_mtime(self):
        obj = self.portal['my-image']
        obj1 = self.portal['my-image1']
        obj2 = self.portal['my-image2']

        tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                       ('collective.cover.image',
                                                        'test-image-tile',))
        tile.populate_with_object(obj)
        self.assertTrue('image_mtime' in tile.data)
        mtime = tile.data['image_mtime']

        tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                       ('collective.cover.image',
                                                        'test-image-tile',))
        tile.populate_with_object(obj1)
        tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                       ('collective.cover.image',
                                                        'test-image-tile',))
        self.assertTrue('image_mtime' in tile.data)
        self.assertNotEqual(tile.data['image_mtime'], mtime)

        tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                       ('collective.cover.image',
                                                        'test-image-tile',))
        tile.populate_with_object(obj2)
        self.assertTrue('image_mtime' in tile.data)
        self.assertNotEqual(tile.data['image_mtime'], mtime)

    def test_image_traversal(self):
        obj = self.portal['my-image']
        obj.setImage(generate_jpeg(1024, 768))
        self.tile.populate_with_object(obj)
        image = self.layer['portal'].restrictedTraverse(
            '@@%s/%s/@@images' %
            ('collective.cover.image',
             'test-image-tile',)).publishTraverse(self.request, 'image')
        img = Image.open(image.index_html())
        self.assertEqual(img.size, (1024, 768))

    def test_image_scale(self):
        obj = self.portal['my-image']
        obj.setImage(generate_jpeg(1024, 768))
        self.tile.populate_with_object(obj)
        scales = self.layer['portal'].restrictedTraverse('@@%s/%s/@@images' %
                                                         ('collective.cover.image',
                                                          'test-image-tile',))
        scale_mini = scales.scale('image', scale='mini')
        img = Image.open(scale_mini.index_html())
        self.assertEqual(img.size, (200, 150))
