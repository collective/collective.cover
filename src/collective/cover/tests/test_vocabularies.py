# -*- coding: utf-8 -*-
from collective.cover.config import IS_PLONE_5
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

    def test_layouts_vocabulary(self):
        name = 'collective.cover.AvailableLayouts'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        layouts = vocabulary(self.portal)
        self.assertEqual(len(layouts), 4)
        self.assertIn(u'Layout A', layouts)
        self.assertIn(u'Layout B', layouts)
        self.assertIn(u'Layout C', layouts)
        self.assertIn(u'Empty layout', layouts)

    def test_available_tiles_vocabulary(self):
        name = 'collective.cover.AvailableTiles'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        tiles = vocabulary(self.portal)
        expected = [
            'collective.cover.banner',
            'collective.cover.basic',
            'collective.cover.calendar',
            'collective.cover.carousel',
            'collective.cover.collection',
            'collective.cover.contentbody',
            'collective.cover.embed',
            'collective.cover.file',
            'collective.cover.list',
            'collective.cover.richtext',
        ]

        # FIXME: https://github.com/collective/collective.cover/issues/633
        if IS_PLONE_5:
            expected.remove('collective.cover.calendar')

        self.assertEqual(len(tiles), len(expected))
        for i in expected:
            self.assertIn(i, tiles)

    def test_enabled_tiles_vocabulary(self):
        name = 'collective.cover.EnabledTiles'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        tiles = vocabulary(self.portal)
        expected = [
            'collective.cover.banner',
            'collective.cover.basic',
            'collective.cover.calendar',
            'collective.cover.carousel',
            'collective.cover.collection',
            'collective.cover.contentbody',
            'collective.cover.embed',
            'collective.cover.file',
            'collective.cover.list',
            'collective.cover.pfg',  # FIXME: https://github.com/collective/collective.cover/issues/194
            'collective.cover.richtext',
        ]

        # FIXME: https://github.com/collective/collective.cover/issues/633
        if IS_PLONE_5:
            expected.remove('collective.cover.calendar')

        self.assertEqual(len(tiles), len(expected))
        for i in expected:
            self.assertIn(i, tiles)

    def test_available_content_types_vocabulary(self):
        name = 'collective.cover.AvailableContentTypes'
        vocabulary = queryUtility(IVocabularyFactory, name)
        self.assertIsNotNone(vocabulary)
        available_content_types = vocabulary(self.portal)
        self.assertTrue(len(available_content_types) > 0)
        self.assertNotIn(u'collective.cover.content', available_content_types)

    def test_tile_styles_vocabulary(self):
        name = 'collective.cover.TileStyles'
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
        name = 'collective.cover.GridSystems'
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
