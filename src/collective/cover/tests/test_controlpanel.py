# -*- coding: utf-8 -*-

from collective.cover.config import DEFAULT_AVAILABLE_TILES
from collective.cover.config import DEFAULT_SEARCHABLE_CONTENT_TYPES
from collective.cover.config import PROJECTNAME
from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import INTEGRATION_TESTING
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class ControlPanelTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.controlpanel = self.portal['portal_controlpanel']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_controlpanel_has_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='cover-settings')
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@cover-settings')

    def test_controlpanel_installed(self):
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertIn('cover', actions)

    def test_controlpanel_removed_on_uninstall(self):
        qi = self.portal['portal_quickinstaller']
        qi.uninstallProducts(products=[PROJECTNAME])
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertNotIn('cover', actions)


class RegistryTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(ICoverSettings)

    def test_sections_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'layouts'))
        self.assertIsNotNone(self.settings.layouts)

    def test_available_tiles_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'available_tiles'))
        self.assertListEqual(
            self.settings.available_tiles, DEFAULT_AVAILABLE_TILES)

    def test_searchable_content_types_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'searchable_content_types'))
        self.assertListEqual(self.settings.searchable_content_types,
                             DEFAULT_SEARCHABLE_CONTENT_TYPES)

    def test_styles_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'styles'))
        self.assertSetEqual(
            self.settings.styles,
            set(['-Default-|tile-default',
                 'Border|tile-edge',
                 'Dark Background|tile-dark',
                 'Shadow|tile-shadow'])
        )

    def test_records_removed_on_uninstall(self):
        qi = self.portal['portal_quickinstaller']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        qi.uninstallProducts(products=[PROJECTNAME])

        BASE_REGISTRY = 'collective.cover.controlpanel.ICoverSettings.'
        records = [
            BASE_REGISTRY + 'layouts',
            BASE_REGISTRY + 'available_tiles',
            BASE_REGISTRY + 'searchable_content_types',
            BASE_REGISTRY + 'styles',
        ]

        for r in records:
            self.assertNotIn(r, self.registry)
