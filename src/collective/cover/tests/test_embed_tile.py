# -*- coding: utf-8 -*-
from collective.cover.interfaces import ISearchableText
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.embed import EmbedTile
from collective.cover.tiles.embed import IEmbedTile
from mock import Mock
from zope.component import queryAdapter

import unittest


class EmbedTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(EmbedTileTestCase, self).setUp()
        self.tile = EmbedTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.embed'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IEmbedTile
        self.klass = EmbedTile
        super(EmbedTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertFalse(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), [])

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_render_empty(self):
        msg = u'Please edit the tile to add the code to be embedded.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_seachable_text(self):
        searchable = queryAdapter(self.tile, ISearchableText)
        self.tile.data['title'] = 'custom title'
        self.tile.data['description'] = 'custom description'
        self.assertEqual(searchable.SearchableText(), 'custom title custom description')
