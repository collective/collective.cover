# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.composition.config import PROJECTNAME
from collective.composition.testing import INTEGRATION_TESTING

JS = [
    '++resource++collective.composition/bootstrap.min.js',
#    '++resource++collective.composition/composition.js',
#    '++resource++collective.composition/layout_base.js',
#    '++resource++collective.composition/layout_edit.js',
    '++resource++collective.composition/screenlets.js',
    ]

CSS = [
    '++resource++collective.composition/bootstrap.min.css',
#    '++resource++collective.composition/composition.css',
#    '++resource++collective.composition/layout_edit.css',
    '++resource++collective.composition/screenlets.css',
    ]


class InstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = getattr(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_jsregistry(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id in JS:
            self.assertTrue(id in resource_ids, '%s not installed' % id)

    def test_cssregistry(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for id in CSS:
            self.assertTrue(id in resource_ids, '%s not installed' % id)


class UninstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.qi = getattr(self.portal, 'portal_quickinstaller')
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_jsregistry_removed(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id in JS:
            self.assertTrue(id not in resource_ids, '%s not removed' % id)

    def test_cssregistry_removed(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for id in CSS:
            self.assertTrue(id not in resource_ids, '%s not removed' % id)
