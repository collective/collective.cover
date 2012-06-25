# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.composition.config import PROJECTNAME
from collective.composition.testing import INTEGRATION_TESTING

JS = [
    'src/collective/composition/static/bootstrap.min.js',
    'src/collective/composition/static/composition.js',
    'src/collective/composition/static/jquery.contextmenu.js',
    'src/collective/composition/static/layout_base.js',
    'src/collective/composition/static/layout_edit.js',
    'src/collective/composition/static/screenlets.js',
    ]

CSS = [
    'src/collective/composition/static/bootstrap.min.css',
    'src/collective/composition/static/composition.css',
    'src/collective/composition/static/jquery.contextmenu.css',
    'src/collective/composition/static/layout_edit.css',
    'src/collective/composition/static/screenlets.css',
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
