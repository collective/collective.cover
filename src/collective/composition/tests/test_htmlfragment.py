# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI

from collective.composition.html_fragment import IHTMLFragment
from collective.composition.testing import INTEGRATION_TESTING


class IntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

    def test_adding(self):
        self.folder.invokeFactory('collective.composition.htmlfragment', 'hf1')
        hf1 = self.folder['hf1']
        self.failUnless(IHTMLFragment.providedBy(hf1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='collective.composition.htmlfragment')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='collective.composition.htmlfragment')
        schema = fti.lookupSchema()
        self.assertEquals(IHTMLFragment, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='collective.composition.htmlfragment')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IHTMLFragment.providedBy(new_object))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
