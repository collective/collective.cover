# -*- coding: utf-8 -*-
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from Products.CMFCore.exceptions import BadRequest

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
        self.request.form['uid'] = obj.UID()
        self.assertIn(u'My document', view())

        obj = self.portal['my-news-item']
        self.request.form['uid'] = obj.UID()
        self.assertIn(u'Test news item', view())


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
        self.request.form['uid'] = obj.UID()
        self.assertNotIn(u'My document', view())
