# -*- coding: utf-8 -*-
from collective.cover.interfaces import ISearchableText
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.richtext import IRichTextTile
from collective.cover.tiles.richtext import RichTextTile
from mock import Mock
from plone.app.textfield.value import RichTextValue
from zope.component import queryAdapter

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

    def test_render_empty(self):
        msg = 'Please edit the tile to enter some text.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_render(self):
        from collective.cover.tests.utils import set_text_field
        text = '<p>My document text...</p>'
        obj = self.portal['my-document']
        set_text_field(obj, text)  # handle Archetypes and Dexterity
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn(text, rendered)

    def test_seachable_text(self):
        searchable = queryAdapter(self.tile, ISearchableText)
        text = '<p>My document text...</p>'
        value = RichTextValue(
            raw=text,
            mimeType='text/x-html-safe',
            outputMimeType='text/x-html-safe'
        )
        self.tile.data['text'] = value
        self.assertEqual(searchable.SearchableText(), 'My document text...')
