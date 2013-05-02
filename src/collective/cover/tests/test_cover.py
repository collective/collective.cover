# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.lockingbehavior.behaviors import ILocking
from plone.app.stagingbehavior.interfaces import IStagingSupport

from collective.cover.content import ICover
from collective.cover.testing import INTEGRATION_TESTING


class CoverIntegrationTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('collective.cover.content', 'c1',
                                  template_layout='Layout A')
        self.c1 = self.folder['c1']
        self.layout_edit = self.c1.restrictedTraverse('layoutedit')

    def test_adding(self):
        self.assertTrue(ICover.providedBy(self.c1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='collective.cover.content')
        self.assertNotEqual(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='collective.cover.content')
        schema = fti.lookupSchema()
        self.assertEqual(ICover, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='collective.cover.content')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ICover.providedBy(new_object))

    def test_exclude_from_navigation_behavior(self):
        self.assertTrue(IExcludeFromNavigation.providedBy(self.c1))

    def test_locking_behavior(self):
        self.assertTrue(ILocking.providedBy(self.c1))

    def test_staging_behavior(self):
        self.assertTrue(IStagingSupport.providedBy(self.c1))

    def test_cover_selectable_as_folder_default_view(self):
        self.folder.setDefaultPage('c1')
        self.assertEqual(self.folder.default_page, 'c1')

    def test_export_permission(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.assertTrue(self.layout_edit.can_export_layout())
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertFalse(self.layout_edit.can_export_layout())
