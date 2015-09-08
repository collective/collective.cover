# -*- coding: utf-8 -*-

from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class VocabulariesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        qi = self.portal['portal_quickinstaller']
        self.has_pfg = False
        if qi.isProductInstalled('Products.PloneFormGen'):
            self.has_pfg = True

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
        self.assertEqual(len(tiles), 9)
        self.assertIn(u'collective.cover.banner', tiles)
        self.assertIn(u'collective.cover.basic', tiles)
        self.assertIn(u'collective.cover.carousel', tiles)
        self.assertIn(u'collective.cover.collection', tiles)
        self.assertIn(u'collective.cover.contentbody', tiles)
        self.assertIn(u'collective.cover.embed', tiles)
        self.assertIn(u'collective.cover.file', tiles)
        self.assertIn(u'collective.cover.list', tiles)
        self.assertIn(u'collective.cover.richtext', tiles)

    def test_enabled_tiles_count(self):
        name = u'collective.cover.EnabledTiles'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        tiles = vocabulary(self.portal)
        tile_count = 10 if self.has_pfg else 9

        self.assertEqual(len(tiles), tile_count)

    def test_enabled_tiles_vocabulary(self):
        name = u'collective.cover.EnabledTiles'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        tiles = vocabulary(self.portal)

        self.assertIn(u'collective.cover.banner', tiles)
        self.assertIn(u'collective.cover.basic', tiles)
        self.assertIn(u'collective.cover.carousel', tiles)
        self.assertIn(u'collective.cover.collection', tiles)
        self.assertIn(u'collective.cover.contentbody', tiles)
        self.assertIn(u'collective.cover.embed', tiles)
        self.assertIn(u'collective.cover.file', tiles)
        self.assertIn(u'collective.cover.list', tiles)
        self.assertIn(u'collective.cover.richtext', tiles)
        # XXX: https://github.com/collective/collective.cover/issues/81
        # standard tiles are not enabled... yet
        self.assertNotIn(u'plone.app.imagetile', tiles)
        self.assertNotIn(u'plone.app.texttile', tiles)

    def test_pfg_tile_enabled(self):
        if not self.has_pfg:
            return
        name = u'collective.cover.EnabledTiles'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        tiles = vocabulary(self.portal)

        # FIXME see: https://github.com/collective/collective.cover/issues/194
        self.assertIn(u'collective.cover.pfg', tiles)

    def test_available_content_types_vocabulary(self):
        name = u'collective.cover.AvailableContentTypes'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        available_content_types = vocabulary(self.portal)
        self.assertTrue(len(available_content_types) > 0)
        self.assertNotIn(u'collective.cover.content', available_content_types)

    def test_tile_styles_vocabulary(self):
        name = u'collective.cover.TileStyles'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        # in the beginning the vocabulary should contain the default styles
        # and the default u"tile-default" style is always first
        styles = vocabulary(self.portal)
        self.assertEqual(len(styles), 4)
        self.assertEqual(styles.by_value.keys()[0], u'tile-default')
        # let's try to put some other values on it
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        settings.styles = set([
            ' red background | redTile ',  # test trimming
            'green background|greenTile',
            'blue background|blueTile',
        ])
        styles = vocabulary(self.portal)
        self.assertIn('redTile', styles.by_value)

        # although default style is not set, vocabulary inserts it first
        self.assertEqual(len(styles), 4)
        self.assertEqual(styles.by_value.keys()[0], u'tile-default')
        # adding a couple of not well formatted items result in no option
        # (except for the default one)
        settings.styles = set(['not well formatted'])
        styles = vocabulary(self.portal)
        self.assertEqual(len(styles), 1)
        self.assertEqual(styles.by_value.keys()[0], u'tile-default')

    def test_grid_systems(self):
        name = u'collective.cover.GridSystems'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)

        # Our default grid system must be in the vocabulary.
        grids = vocabulary(self.portal)
        self.assertEqual(len(grids), 3)
        self.assertIn(u'bootstrap3', grids)
        self.assertIn(u'bootstrap2', grids)
        self.assertIn(u'deco16_grid', grids)
        self.assertEqual(grids.getTerm('bootstrap3').title, u'Bootstrap 3')
        self.assertEqual(grids.getTerm('bootstrap2').title, u'Bootstrap 2')
        self.assertEqual(grids.getTerm('deco16_grid').title, u'Deco (16 columns)')
