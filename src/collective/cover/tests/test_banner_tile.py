# -*- coding: utf-8 -*-
from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.banner import BannerTile
from collective.cover.tiles.banner import IBannerTile
from lxml import etree  # nosec
from mock import Mock
from plone.tiles.interfaces import ITileDataManager

import six
import unittest


class BannerTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(BannerTileTestCase, self).setUp()
        self.tile = BannerTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.banner'
        self.tile.id = u'test'

    @property
    def get_tile(self):
        """Return a new instance of the tile to avoid data caching."""
        return self.cover.restrictedTraverse(
            '@@{0}/{1}'.format(self.tile.__name__, self.tile.id))

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IBannerTile
        self.klass = BannerTile
        super(BannerTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ALL_CONTENT_TYPES)

    def test_populate_with_image_object_text(self):
        """We must store unicode always on schema.TextLine and schema.Text
        fields to avoid UnicodeDecodeError.
        """
        title = u'El veloz murciélago hindú comía feliz cardillo y kiwi'
        obj = self.portal['my-image']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.data.get('title'), title)
        self.assertIsInstance(self.tile.data.get('title'), six.text_type)
        self.assertTrue(self.tile.has_image)
        self.assertIsNotNone(self.tile.getRemoteUrl())

    def test_populate_tile_with_image_object_string(self):
        """This test complements test_populate_with_image_object_unicode
        using strings instead of unicode objects.
        """
        title = 'The quick brown fox jumps over the lazy dog'
        obj = self.portal['my-image']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(
            six.text_type(title, 'utf-8'), self.tile.data.get('title'))
        self.assertTrue(self.tile.has_image)
        self.assertIsNotNone(self.tile.getRemoteUrl())

    def test_populate_with_link_object_text(self):
        """We must store unicode always on schema.TextLine and schema.Text
        fields to avoid UnicodeDecodeError.
        """
        title = u'El veloz murciélago hindú comía feliz cardillo y kiwi'
        obj = self.portal['my-link']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.data.get('title'), title)
        self.assertIsInstance(self.tile.data.get('title'), six.text_type)
        self.assertFalse(self.tile.has_image)
        self.assertEqual(self.tile.getRemoteUrl(), 'http://plone.org')

    def test_populate_tile_with_link_object_string(self):
        """This test complements test_populate_with_link_object_unicode
        using strings instead of unicode objects.
        """
        title = 'The quick brown fox jumps over the lazy dog'
        obj = self.portal['my-link']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(
            six.text_type(title, 'utf-8'), self.tile.data.get('title'))
        self.assertFalse(self.tile.has_image)
        self.assertEqual(self.tile.getRemoteUrl(), 'http://plone.org')

    def test_render_empty(self):
        msg = 'Drag&amp;drop an image or link here to populate the tile.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_render_with_image(self):
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        html = etree.HTML(self.tile())
        img = html.find('*//img')
        self.assertIsNotNone(img)
        self.assertIn('alt', img.attrib)
        self.assertEqual(img.attrib['alt'], obj.Description())

        # set alternate text
        alt_text = u'Murciélago hindú'
        self.tile.data['alt_text'] = alt_text
        html = etree.HTML(self.tile())
        img = html.find('*//img')
        self.assertIsNotNone(img)
        self.assertIn('alt', img.attrib)
        self.assertEqual(img.attrib['alt'], alt_text)

    def test_render_with_link(self):
        obj = self.portal['my-link']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertNotIn('<img ', rendered)
        self.assertIn('<a href="http://plone.org">Test link</a>', rendered)

    def test_getRemoteUrl(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        expected = 'http://nohost/plone/my-news-item'
        self.assertEqual(self.tile.getRemoteUrl(), expected)

    def test_getRemoteUrl_link(self):
        # on links we should get its remote URL
        obj = self.portal['my-link']
        self.tile.populate_with_object(obj)
        expected = 'http://plone.org'
        self.assertEqual(self.tile.getRemoteUrl(), expected)

    def test_getRemoteUrl_view_action(self):
        # on some content types we should add '/view' to the URL
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        expected = 'http://nohost/plone/my-image/view'
        self.assertEqual(self.tile.getRemoteUrl(), expected)

    def test_getRemoteUrl_render(self):
        # the URL must be rendered normally
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        html = etree.HTML(self.tile())
        a = html.find('*//a')
        expected = 'http://nohost/plone/my-news-item'
        self.assertEqual(a.attrib['href'], expected)

    def test_getRemoteUrl_render_edited(self):
        # the alternate URL must be rendered
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        remote_url = 'http://example.org/'
        data_mgr = ITileDataManager(self.tile)
        data = data_mgr.get()
        data['remote_url'] = remote_url
        data_mgr.set(data)
        tile = self.get_tile
        html = etree.HTML(tile())
        a = html.find('*//a')
        self.assertEqual(a.attrib['href'], remote_url)

    def test_getRemoteUrl_render_empty(self):
        # no anchor is rendered if URL field is empty
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        data_mgr = ITileDataManager(self.tile)
        data = data_mgr.get()
        data['remote_url'] = u''
        data_mgr.set(data)
        tile = self.get_tile
        html = etree.HTML(tile())
        a = html.find('*//a')
        self.assertIsNone(a)
