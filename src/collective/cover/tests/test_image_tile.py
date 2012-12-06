# -*- coding: utf-8 -*-

import unittest2 as unittest
from PIL import Image
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from collective.cover.testing import INTEGRATION_TESTING, generate_jpeg
from collective.cover.tiles.image import ImageTile
from collective.cover.tiles.base import IPersistentCoverTile


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

    def test_image_traverser(self):
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        scales = self.layer['portal'].restrictedTraverse('@@%s/%s/@@images' %
                                                         ('collective.cover.image',
                                                          'test-image-tile',))
        img = scales.scale('image')
        self.assertEqual(str(self.tile.data['image'].data),
                         str(img.index_html().read()))

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
        self.assertEqual(str(tile.data['image'].data),
                         str(obj1.getImage()))
        scales = self.layer['portal'].restrictedTraverse('@@%s/%s/@@images' %
                                                         ('collective.cover.image',
                                                          'test-image-tile',))
        img = scales.scale('image')
        self.assertEqual(str(tile.data['image'].data),
                         str(img.index_html().read()))
        self.assertEqual(str(img.index_html().read()),
                         str(obj1.getImage()))

        tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                       ('collective.cover.image',
                                                        'test-image-tile',))
        tile.populate_with_object(obj)
        rendered = tile()
        self.assertTrue('test-image-tile/@@images' in rendered)
        self.assertNotEqual(str(tile.data['image'].data),
                            str(obj1.getImage()))
        self.assertEqual(str(tile.data['image'].data),
                         str(obj.getImage()))
        scales = self.layer['portal'].restrictedTraverse('@@%s/%s/@@images' %
                                                         ('collective.cover.image',
                                                          'test-image-tile',))
        img = scales.scale('image')
        self.assertEqual(str(tile.data['image'].data),
                         str(img.index_html().read()))
        self.assertEqual(str(img.index_html().read()),
                         str(obj.getImage()))

        tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                       ('collective.cover.image',
                                                        'test-image-tile',))
        tile.populate_with_object(obj2)
        rendered = tile()
        self.assertTrue('test-image-tile/@@images' in rendered)
        self.assertNotEqual(str(tile.data['image'].data),
                            str(obj1.getImage()))
        self.assertNotEqual(str(tile.data['image'].data),
                            str(obj.getImage()))
        self.assertEqual(str(tile.data['image'].data),
                         str(obj2.getImage()))
        scales = self.layer['portal'].restrictedTraverse('@@%s/%s/@@images' %
                                                         ('collective.cover.image',
                                                          'test-image-tile',))
        img = scales.scale('image')
        self.assertEqual(str(tile.data['image'].data),
                         str(img.index_html().read()))
        self.assertEqual(str(img.index_html().read()),
                         str(obj2.getImage()))

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
