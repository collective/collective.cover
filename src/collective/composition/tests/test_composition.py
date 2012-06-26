# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.app.lockingbehavior.behaviors import ILocking

from collective.composition.composition import IComposition
from collective.composition.testing import INTEGRATION_TESTING


class CompositionIntegrationTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

    def test_adding(self):
        self.folder.invokeFactory('collective.composition.composition', 'c1',
                                  template_layout='Layout A')
        c1 = self.folder['c1']
        self.assertTrue(IComposition.providedBy(c1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='collective.composition.composition')
        self.assertNotEqual(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='collective.composition.composition')
        schema = fti.lookupSchema()
        self.assertEqual(IComposition, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='collective.composition.composition')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IComposition.providedBy(new_object))

    def test_locking_behavior(self):
        self.folder.invokeFactory('collective.composition.composition', 'c1',
                                  template_layout='Layout A')
        c1 = self.folder['c1']
        self.assertTrue(ILocking.providedBy(c1))
