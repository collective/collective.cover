# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class VocabulariesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_layouts_vocabulary(self):
        name = u'collective.cover.AvailableLayouts'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        layouts = vocabulary(self.portal)
        self.assertEqual(len(layouts), 4)
        self.assertIn(u'Layout A', layouts)
        self.assertIn(u'Layout B', layouts)
        self.assertIn(u'Layout C', layouts)
        self.assertIn(u'Empty layout', layouts)

    def test_available_tiles_vocabulary(self):
        name = u'collective.cover.AvailableTiles'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        tiles = vocabulary(self.portal)
        self.assertEqual(len(tiles), 11)
        self.assertIn(u'collective.cover.basic', tiles)
        self.assertIn(u'collective.cover.carousel', tiles)
        self.assertIn(u'collective.cover.collection', tiles)
        self.assertIn(u'collective.cover.contentbody', tiles)
        self.assertIn(u'collective.cover.embed', tiles)
        self.assertIn(u'collective.cover.file', tiles)
        self.assertIn(u'collective.cover.image', tiles)
        self.assertIn(u'collective.cover.link', tiles)
        self.assertIn(u'collective.cover.list', tiles)
        self.assertIn(u'collective.cover.pfg', tiles)
        self.assertIn(u'collective.cover.richtext', tiles)
        # XXX: https://github.com/collective/collective.cover/issues/81
        #self.assertIn(u'plone.app.imagetile', tiles)
        #self.assertIn(u'plone.app.texttile', tiles)

    def test_user_friendly_types_vocabulary(self):
        name = u'collective.cover.AvailableContentTypes'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        friendly_types = vocabulary(self.portal)
        self.assertTrue(len(friendly_types) > 0)
        self.assertNotInIn(u'collective.cover.content', friendly_types)
