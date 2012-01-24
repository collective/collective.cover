# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI

from collective.composition.html_fragment import IHTMLFragment
from collective.composition.testing import INTEGRATION_TESTING


class HTMLFragmentIntegrationTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

    def test_adding(self): 
        #Adding to self.portal and to self.folder raises ValueError
        self.assertRaises(
            ValueError,
            self.portal.invokeFactory,
            *('collective.composition.htmlfragment', 'hf1')
        )
        self.assertRaises(
            ValueError,
            self.folder.invokeFactory,
           *('collective.composition.htmlfragment', 'hf1')
        )

        #So, first we need to add the the composition container
        self.folder.invokeFactory('collective.composition.composition', 'c1')
        c1 = self.folder['c1']

        #Now we can add the htmlfragment to the composition
        c1.invokeFactory('collective.composition.htmlfragment', 'hf1')
        hf1 = c1['hf1']

        #Now test
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
