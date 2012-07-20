# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import queryUtility

from zope.schema.interfaces import IVocabularyFactory

from collective.cover.testing import INTEGRATION_TESTING


class VocabulariesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_layouts_vocabulary(self):
        name = u'collective.cover.AvailableLayouts'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertTrue(vocabulary is not None)
        layouts = vocabulary(self.portal)
        self.assertEqual(len(layouts), 3)
        self.assertTrue(u'Layout A' in layouts)
        self.assertTrue(u'Layout B' in layouts)
        self.assertTrue(u'Layout C' in layouts)

    def test_tiles_vocabulary(self):
        name = u'collective.cover.AvailableTiles'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertTrue(vocabulary is not None)
        tiles = vocabulary(self.portal)
        self.assertEqual(len(tiles), 8)
        self.assertTrue(u'collective.cover.basic' in tiles)
        self.assertTrue(u'collective.cover.carousel' in tiles)
        self.assertTrue(u'collective.cover.collection' in tiles)
        self.assertTrue(u'collective.cover.embed' in tiles)
        self.assertTrue(u'collective.cover.file' in tiles)
        self.assertTrue(u'collective.cover.link' in tiles)
        self.assertTrue(u'collective.cover.list' in tiles)
        self.assertTrue(u'collective.cover.richtext' in tiles)

    def test_user_friendly_types_vocabulary(self):
        name = u'collective.cover.AvailableContentTypes'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertTrue(vocabulary is not None)
        friendly_types = vocabulary(self.portal)
        self.assertTrue(len(friendly_types) > 0)
        self.assertTrue(u'collective.cover.content' not in friendly_types)
