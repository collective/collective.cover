# -*- coding: utf-8 -*-

from collective.cover.interfaces import ICoverLayer
from collective.cover.tiles.list import ListTile
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from zope.interface import directlyProvides

import unittest


class BrowserViewsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        directlyProvides(self.request, ICoverLayer)

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(
                self.portal, 'Folder', 'test-folder')

        self.c1 = api.content.create(
            self.folder,
            'collective.cover.content',
            'c1',
            title='Front page',
            description='Should I see this?',
        )

    def test_default_view_registration(self):
        portal_types = self.portal['portal_types']
        default_view = portal_types['collective.cover.content'].default_view
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertEqual(default_view, u'view')
        self.assertIn(u'view', view_methods)

    @unittest.expectedFailure  # FIXME: why is this failing?
    def test_default_view_render(self):
        view = api.content.get_view(u'view', self.c1, self.request)
        rendered_html = view.render()
        # default view should not show title, description or viewlets
        self.assertNotIn('Front page', rendered_html)
        self.assertNotIn('Should I see this?', rendered_html)

    def test_alternate_view_registration(self):
        portal_types = self.portal['portal_types']
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertIn(u'standard', view_methods)

    @unittest.expectedFailure  # FIXME: why is this failing?
    def test_alternate_view_render(self):
        view = api.content.get_view(u'standard', self.c1, self.request)
        rendered_html = view.render()
        # default view should show title, description and viewlets
        self.assertIn('Front page', rendered_html)
        self.assertIn('Should I see this?', rendered_html)


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
        self.request.form['uid'] = obj1.UID()
        view = api.content.get_view(
            u'removeitemfromlisttile', self.cover, self.request)

        self.assertIn(obj1, tile.results())
        view.render()
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
