# -*- coding: utf-8 -*-
from collective.cover.config import IS_PLONE_5
from collective.cover.config import PROJECTNAME
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.browserlayer.utils import registered_layers

import unittest


JS = [
    '++resource++collective.cover/js/contentchooser.js',
    '++resource++collective.js.bootstrap/js/bootstrap.min.js',
    '++resource++collective.cover/js/vendor/jquery.endless-scroll.js',
]

CSS = [
    '++resource++collective.cover/css/contentchooser.css',
    '++resource++collective.cover/css/cover.css',
]


class InstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']

    def test_installed(self):
        self.assertTrue(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('ICoverLayer', layers)

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
    def test_jsregistry(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id in JS:
            self.assertIn(id, resource_ids, '{0} not installed'.format(id))

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
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


class UninstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('ICoverLayer', layers)

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
    def test_jsregistry_removed(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id in JS:
            self.assertNotIn(id, resource_ids, '{0} not removed'.format(id))

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
    def test_cssregistry_removed(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for id in CSS:
            self.assertNotIn(id, resource_ids, '{0} not removed'.format(id))
