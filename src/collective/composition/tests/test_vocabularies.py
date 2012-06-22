# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import queryUtility

from zope.schema.interfaces import IVocabularyFactory

from collective.composition.testing import INTEGRATION_TESTING


class VocabulariesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_layouts_vocabulary(self):
        name = 'collective.composition.vocabularies.layouts'
        util = queryUtility(IVocabularyFactory, name)
        self.assertTrue(util is not None)
        layouts = util(self.portal)
        self.assertEqual(len(layouts), 1)

    def test_portlets_vocabulary(self):
        name = 'collective.composition.vocabularies.portlets'
        util = queryUtility(IVocabularyFactory, name)
        self.assertTrue(util is not None)
        portlets = util(self.portal)
        self.assertEqual(len(portlets), 0)
