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
        self.assertEqual(len(tiles), 10)
        self.assertIn(u'collective.cover.basic', tiles)
        self.assertIn(u'collective.cover.carousel', tiles)
        self.assertIn(u'collective.cover.collection', tiles)
        self.assertIn(u'collective.cover.contentbody', tiles)
        self.assertIn(u'collective.cover.embed', tiles)
        self.assertIn(u'collective.cover.file', tiles)
        self.assertIn(u'collective.cover.image', tiles)
        self.assertIn(u'collective.cover.link', tiles)
        self.assertIn(u'collective.cover.list', tiles)
        self.assertIn(u'collective.cover.richtext', tiles)

    def test_enabled_tiles_vocabulary(self):
        name = u'collective.cover.EnabledTiles'
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
        # FIXME see: https://github.com/collective/collective.cover/issues/194
        self.assertIn(u'collective.cover.pfg', tiles)
        self.assertIn(u'collective.cover.richtext', tiles)
        # XXX: https://github.com/collective/collective.cover/issues/81
        # standard tiles are not enabled... yet
        self.assertNotIn(u'plone.app.imagetile', tiles)
        self.assertNotIn(u'plone.app.texttile', tiles)

    def test_available_content_types_vocabulary(self):
        name = u'collective.cover.AvailableContentTypes'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        available_content_types = vocabulary(self.portal)
        self.assertTrue(len(available_content_types) > 0)
        self.assertNotIn(u'collective.cover.content', available_content_types)
