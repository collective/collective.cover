# -*- coding: utf-8 -*-
from collective.cover.interfaces import ICoverLayer
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.list import ListTile
from lxml import etree
from plone import api
from plone.app.testing import logout
from zope.interface import alsoProvides

import unittest


class BrowserViewsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, ICoverLayer)

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(
                self.portal, 'Folder', 'test-folder')

        self.c1 = api.content.create(
            self.folder,
            'collective.cover.content',
            'c1',
            title='My Title',
            description='My Description',
            template_layout='Layout A',
        )

    def test_default_view_registration(self):
        portal_types = self.portal['portal_types']
        default_view = portal_types['collective.cover.content'].default_view
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertEqual(default_view, u'view')
        self.assertIn(u'view', view_methods)

    def test_default_view_render(self):
        view = api.content.get_view(u'view', self.c1, self.request)
        html = etree.HTML(view())
        # default view should not show title, description or viewlets
        self.assertEqual(
            len(html.xpath('.//h1[contains(text(),"My Title")]')), 0)
        self.assertEqual(
            len(html.xpath('.//div[contains(text(),"My Description")]')), 0)

    def test_default_view_forbids_image_indexing(self):
        view = api.content.get_view(u'view', self.c1, self.request)
        view()  # render the view to get the response
        response = self.request.RESPONSE
        self.assertIn('x-robots-tag', response.headers)
        self.assertEqual(response.getHeader('x-robots-tag'), 'noimageindex')

    def test_alternate_view_registration(self):
        portal_types = self.portal['portal_types']
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertIn(u'standard', view_methods)

    def test_alternate_view_render(self):
        view = api.content.get_view(u'standard', self.c1, self.request)
        html = etree.HTML(view())
        # alternate view should show title, description and viewlets
        self.assertEqual(
            len(html.xpath('.//h1[contains(text(),"My Title")]')), 1)
        self.assertEqual(
            len(html.xpath('.//div[contains(text(),"My Description")]')), 1)

    def test_body_class(self):
        view = api.content.get_view(u'view', self.c1, self.request)
        html = etree.HTML(view())
        self.assertEqual(
            len(html.xpath('.//body[contains(@class, "cover-layout-layout-a")]')), 1)

        view = api.content.get_view(u'standard', self.c1, self.request)
        html = etree.HTML(view())
        self.assertEqual(
            len(html.xpath('.//body[contains(@class, "cover-layout-layout-a")]')), 1)

    # @@updatetile
    def test_update_tile_view(self):
        # This view should be available to Anonymous users
        logout()
        # valid tile-id parameter returns tile
        tile_id = self.c1.list_tiles()[0]  # use a tile on the layout
        self.request.form['tile-id'] = tile_id
        view = self.c1.restrictedTraverse('@@updatetile')
        self.assertNotEqual(view(), u'')
        self.assertEqual(view.request.RESPONSE.status, 200)

    def test_update_tile_view_no_tile_id(self):
        # no tile-id parameter results on Bad Request
        view = api.content.get_view(u'updatetile', self.c1, self.request)
        self.assertEqual(view(), u'')
        self.assertEqual(view.request.RESPONSE.status, 400)

    def test_update_tile_view_invalid_tile_id(self):
        # invalid tile-id parameter results on Bad Request
        self.request.form['tile-id'] = 'invalid'
        view = api.content.get_view(u'updatetile', self.c1, self.request)
        self.assertEqual(view(), u'')
        self.assertEqual(view.request.RESPONSE.status, 400)


class RemoveItemFromListTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            self.cover = api.content.create(
                self.portal, 'collective.cover.content', 'c1')

    # XXX: refactor, this sucks!
    def test_remove_item_from_list_tile(self):
        # add a list tile
        tile = ListTile(self.cover, self.request)
        tile.__name__ = u'collective.cover.list'
        tile.id = u'test'

        # add a couple of objects to the list
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        tile.populate_with_object(obj1)
        tile.populate_with_object(obj2)

        self.request.form['tile-type'] = u'collective.cover.list'
        self.request.form['tile-id'] = u'test'
        self.request.form['uuid'] = obj1.UID()
        view = api.content.get_view(
            u'removeitemfromlisttile', self.cover, self.request)

        self.assertIn(obj1, tile.results())
        view()
        self.assertNotIn(obj1, tile.results())


class ConfigurationViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_configure_tile(self):
        traversal = self.portal.unrestrictedTraverse('@@configure-tile')
        self.assertIsNone(traversal.view)

        with self.assertRaises(KeyError):
            traversal()

        traversal = traversal.publishTraverse(self.request, 'collective.cover.list')
        self.assertEqual(traversal.view.tileType.title, u'List Tile')
        self.assertIsNone(traversal.view.tileId)

        view = traversal.publishTraverse(self.request, '1234')
        self.assertEqual(view.tileId, '1234')

        with self.assertRaises(KeyError):
            traversal.publishTraverse(self.request, 'too much')
