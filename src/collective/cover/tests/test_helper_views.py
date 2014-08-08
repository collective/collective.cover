# -*- coding: utf-8 -*-
from collective.cover.interfaces import ICoverLayer
from collective.cover.tiles.basic import BasicTile
from collective.cover.testing import INTEGRATION_TESTING
from plone import api

import unittest


class UpdateTileContentViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            self.cover = api.content.create(
                self.portal, 'collective.cover.content', 'c1')

    def test_view(self):
        view = self.cover.restrictedTraverse('updatetilecontent')

        self.request.form['tile-type'] = 'collective.cover.basic'
        self.request.form['tile-id'] = 'test'
        obj = self.portal['my-document']
        self.request.form['uid'] = obj.UID()
        self.assertIn(u'My document', view.render())

        obj = self.portal['my-news-item']
        self.request.form['uid'] = obj.UID()
        self.assertIn(u'Test news item', view.render())
