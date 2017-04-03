# -*- coding: utf-8 -*-
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from zExceptions import BadRequest

import unittest


class HelperViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            folder = api.content.create(self.portal, 'Folder', 'folder')

        self.cover = api.content.create(
            folder, 'collective.cover.content', 'c1')


class UpdateTileContentViewTestCase(HelperViewTestCase):

    def test_view(self):
        view = self.cover.restrictedTraverse('updatetilecontent')

        with self.assertRaises(BadRequest):
            view()

        self.request.form['tile-type'] = 'collective.cover.basic'
        self.request.form['tile-id'] = 'test'
        obj = self.portal['my-document']
        self.request.form['uuid'] = obj.UID()
        self.assertIn(u'My document', view())

        obj = self.portal['my-news-item']
        self.request.form['uuid'] = obj.UID()
        self.assertIn(u'Test news item', view())


class MoveTileContentViewTestCase(HelperViewTestCase):

    def test_move_all_content(self):
        view = self.cover.restrictedTraverse('movetilecontent')

        # Test move all content with many items
        origin_tile = self.cover.restrictedTraverse('collective.cover.carousel/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.carousel/target')
        origin_tile.populate_with_object(self.portal['my-image'])
        origin_tile.populate_with_object(self.portal['my-image1'])
        origin_tile.populate_with_object(self.portal['my-image2'])
        self.assertIn(u'my-image', origin_tile())
        self.assertIn(u'my-image1', origin_tile())
        self.assertIn(u'my-image2', origin_tile())
        self.assertNotIn(u'my-image', target_tile())
        self.assertNotIn(u'my-image1', target_tile())
        self.assertNotIn(u'my-image2', target_tile())

        view._move_all_content(origin_tile, target_tile)
        origin_tile = self.cover.restrictedTraverse('collective.cover.carousel/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.carousel/target')
        self.assertNotIn(u'my-image', origin_tile())
        self.assertNotIn(u'my-image1', origin_tile())
        self.assertNotIn(u'my-image2', origin_tile())
        self.assertIn(u'my-image', target_tile())
        self.assertIn(u'my-image1', target_tile())
        self.assertIn(u'my-image2', target_tile())

    def test_move_selected_content(self):
        view = self.cover.restrictedTraverse('movetilecontent')

        # Test move selected content with one item
        origin_tile = self.cover.restrictedTraverse('collective.cover.basic/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.basic/target')
        obj = self.portal['my-document']
        origin_tile.populate_with_object(obj)
        self.assertIn(u'My document', origin_tile())
        self.assertNotIn(u'My document', target_tile())

        view._move_selected_content(origin_tile, target_tile, obj)
        origin_tile = self.cover.restrictedTraverse('collective.cover.basic/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.basic/target')
        self.assertNotIn(u'My document', origin_tile())
        self.assertIn(u'My document', target_tile())

        # Test move selected content with many items
        origin_tile = self.cover.restrictedTraverse('collective.cover.carousel/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.carousel/target')
        obj1 = self.portal['my-image']
        obj2 = self.portal['my-image1']
        obj3 = self.portal['my-image2']
        origin_tile.populate_with_object(obj1)
        origin_tile.populate_with_object(obj2)
        origin_tile.populate_with_object(obj3)
        self.assertIn(u'my-image', origin_tile())
        self.assertIn(u'my-image1', origin_tile())
        self.assertIn(u'my-image2', origin_tile())
        self.assertNotIn(u'my-image', target_tile())
        self.assertNotIn(u'my-image1', target_tile())
        self.assertNotIn(u'my-image2', target_tile())

        view._move_selected_content(origin_tile, target_tile, obj1)
        origin_tile = self.cover.restrictedTraverse('collective.cover.carousel/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.carousel/target')
        self.assertNotIn(u'/my-image/', origin_tile())
        self.assertIn(u'/my-image/', target_tile())

        view._move_selected_content(origin_tile, target_tile, obj2)
        origin_tile = self.cover.restrictedTraverse('collective.cover.carousel/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.carousel/target')
        self.assertNotIn(u'/my-image1/', origin_tile())
        self.assertIn(u'/my-image1/', target_tile())

        view._move_selected_content(origin_tile, target_tile, obj3)
        origin_tile = self.cover.restrictedTraverse('collective.cover.carousel/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.carousel/target')
        self.assertIn(u'/my-image2/', target_tile())
        self.assertNotIn(u'/my-image2/', origin_tile())

    def test_view(self):
        view = self.cover.restrictedTraverse('movetilecontent')
        with self.assertRaises(BadRequest):
            view()

        # Populate origin tile with one item
        origin_tile = self.cover.restrictedTraverse('collective.cover.basic/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.basic/target')
        obj = self.portal['my-document']
        origin_tile.populate_with_object(obj)
        self.assertIn(u'My document', origin_tile())
        self.assertNotIn(u'My document', target_tile())

        # Call the view
        self.request.form['origin-type'] = 'collective.cover.basic'
        self.request.form['origin-id'] = 'origin'
        self.request.form['target-type'] = 'collective.cover.basic'
        self.request.form['target-id'] = 'target'
        self.request.form['uuid'] = obj.UID()
        view()

        # Check if the item moved from origin tile to target tile
        origin_tile = self.cover.restrictedTraverse('collective.cover.basic/origin')
        target_tile = self.cover.restrictedTraverse('collective.cover.basic/target')
        self.assertNotIn(u'My document', origin_tile())
        self.assertIn(u'My document', target_tile())


class RemoveItemFromListTileViewTestCase(HelperViewTestCase):

    def test_view(self):
        view = self.cover.restrictedTraverse('removeitemfromlisttile')

        with self.assertRaises(BadRequest):
            view()

        tile = self.cover.restrictedTraverse('@@collective.cover.list/test')
        tile.populate_with_object(self.portal['my-document'])
        tile.populate_with_object(self.portal['my-image'])
        tile.populate_with_object(self.portal['my-news-item'])

        self.request.form['tile-type'] = 'collective.cover.list'
        self.request.form['tile-id'] = 'test'
        obj = self.portal['my-document']
        self.request.form['uuid'] = obj.UID()
        self.assertNotIn(u'My document', view())
