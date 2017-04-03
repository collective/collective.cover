# -*- coding: utf-8 -*-
from collective.cover.config import DEFAULT_AVAILABLE_TILES
from collective.cover.config import DEFAULT_GRID_SYSTEM
from collective.cover.config import DEFAULT_SEARCHABLE_CONTENT_TYPES
from collective.cover.config import PROJECTNAME
from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


class ControlPanelTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.controlpanel = self.portal['portal_controlpanel']

    def test_controlpanel_has_view(self):
        request = self.layer['request']
        view = api.content.get_view(u'cover-settings', self.portal, request)
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
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECTNAME])
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertNotIn('cover', actions)

    def test_controlpanel_permissions(self):
        roles = ['Manager', 'Site Administrator']
        for r in roles:
            with api.env.adopt_roles([r]):
                configlets = self.controlpanel.enumConfiglets(group='Products')
                configlets = [a['id'] for a in configlets]
                self.assertIn(
                    'cover', configlets, 'configlet not listed for ' + r)


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

    def test_grid_system_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'grid_system'))
        self.assertEqual(
            self.settings.grid_system, DEFAULT_GRID_SYSTEM)

    def test_records_removed_on_uninstall(self):
        qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECTNAME])

        BASE_REGISTRY = 'collective.cover.controlpanel.ICoverSettings.'
        records = [
            BASE_REGISTRY + 'layouts',
            BASE_REGISTRY + 'available_tiles',
            BASE_REGISTRY + 'searchable_content_types',
            BASE_REGISTRY + 'styles',
            BASE_REGISTRY + 'grid_system',
        ]

        for r in records:
            self.assertNotIn(r, self.registry)

    def test_records_not_overwriten_on_reinstall(self):
        """Test changes are not purged on reinstall.
        https://github.com/collective/collective.cover/issues/465
        """
        self.settings.styles = set(['foo'])
        del self.settings.layouts['Empty layout']

        self.assertEqual(len(self.settings.styles), 1)
        self.assertEqual(len(self.settings.layouts), 3)

        qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            qi.reinstallProducts(products=[PROJECTNAME])

        self.assertIn('foo', self.settings.styles)
        self.assertEqual(len(self.settings.styles), 5)
        self.assertIn('Empty layout', self.settings.layouts)
        self.assertEqual(len(self.settings.layouts), 4)
