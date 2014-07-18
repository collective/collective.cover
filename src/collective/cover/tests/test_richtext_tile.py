# -*- coding: utf-8 -*-
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.richtext import IRichTextTile
from collective.cover.tiles.richtext import RichTextTile
from mock import Mock

import unittest


class RichTextTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(RichTextTileTestCase, self).setUp()
        self.tile = RichTextTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.richtext'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IRichTextTile
        self.klass = RichTextTile
        super(RichTextTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['Document'])

    def test_populate_with_object(self):
        self.tile.populate_with_object(self.portal['my-document'])
        self.assertEqual(self.tile.getText(), '')

    def test_render_empty(self):
        msg = 'Please edit the tile to enter some text.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_render(self):
        obj = self.portal['my-document']
        obj.setText('<p>My document text...</p>')
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('<p>My document text...</p>', rendered)
