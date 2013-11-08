# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter

import unittest


class BrowserViewsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory(
            'collective.cover.content',
            'c1',
            title='Front page',
            description='Should I see this?',
        )
        self.c1 = self.folder['c1']

    def test_default_view_registration(self):
        portal_types = self.portal['portal_types']
        default_view = portal_types['collective.cover.content'].default_view
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertEqual(default_view, u'view')
        self.assertIn(u'view', view_methods)

    # FIXME
    @unittest.expectedFailure
    def test_default_view_render(self):
        view = getMultiAdapter((self.c1, self.request), name='view')
        rendered_html = view.render()
        # default view should not show title, description or viewlets
        self.assertNotIn(rendered_html, 'Front page')
        self.assertNotIn(rendered_html, 'Should I see this?')

    def test_alternate_view_registration(self):
        portal_types = self.portal['portal_types']
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertIn(u'standard', view_methods)

    # FIXME
    @unittest.expectedFailure
    def test_alternate_view_render(self):
        view = getMultiAdapter((self.c1, self.request), name='standard')
        rendered_html = view.render()
        # default view should show title, description and viewlets
        self.assertIn(rendered_html, 'Front page')
        self.assertIn(rendered_html, 'Should I see this?')


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
