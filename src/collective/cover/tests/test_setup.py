# -*- coding: utf-8 -*-

from collective.cover.config import PROJECTNAME
from collective.cover.testing import INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.browserlayer.utils import registered_layers

import unittest

JS = [
    '++resource++collective.cover/contentchooser.js',
    '++resource++collective.js.bootstrap/js/bootstrap.min.js',
    '++resource++collective.cover/jquery.endless-scroll.js',
]

CSS = [
    '++resource++collective.cover/contentchooser.css',
    '++resource++collective.cover/cover.css',
]


class InstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = getattr(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('ICoverLayer', layers)

    def test_jsregistry(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id in JS:
            self.assertIn(id, resource_ids, '{0} not installed'.format(id))

    def test_cssregistry(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for id in CSS:
            self.assertIn(id, resource_ids, '{0} not installed'.format(id))

    def test_resources_available(self):
        resources = CSS + JS
        for id in resources:
            res = self.portal.restrictedTraverse(id)
            self.assertTrue(res)

    def test_reinstall_with_changed_registry(self):
        ps = getattr(self.portal, 'portal_setup')
        try:
            ps.runAllImportStepsFromProfile('profile-collective.cover:default')
        except AttributeError:
            self.fail('Reinstall fails when the record was changed')

    def test_can_export_layout_permission(self):
        permission = 'collective.cover: Can Export Layout'
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        expected = ['Manager', 'Site Administrator']
        self.assertListEqual(roles, expected)


class UninstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.qi = getattr(self.portal, 'portal_quickinstaller')
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('ICoverLayer', layers)

    def test_jsregistry_removed(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id in JS:
            self.assertNotIn(id, resource_ids, '{0} not removed'.format(id))

    def test_cssregistry_removed(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for id in CSS:
            self.assertNotIn(id, resource_ids, '{0} not removed'.format(id))
