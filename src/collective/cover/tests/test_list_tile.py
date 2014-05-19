# -*- coding: utf-8 -*-
from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.list import IListTile
from collective.cover.tiles.list import ListTile
from mock import Mock
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID

import unittest


class ListTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(ListTileTestCase, self).setUp()
        self.tile = ListTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.list'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IListTile
        self.klass = ListTile
        super(ListTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_droppable)
        self.assertTrue(self.tile.is_editable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ALL_CONTENT_TYPES)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_crud(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())

        # now we add a couple of objects to the list
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        self.tile.populate_with_object(obj1)
        self.tile.populate_with_object(obj2)
        # tile's data attribute is cached; reinstantiate it
        self.tile = self.cover.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.list', 'test'))
        self.assertEqual(len(self.tile.results()), 2)
        self.assertIn(obj1, self.tile.results())
        self.assertIn(obj2, self.tile.results())

        # next, we replace the list of objects with a different one
        obj3 = self.portal['my-news-item']
        self.tile.replace_with_objects([IUUID(obj3, None)])
        # tile's data attribute is cached; reinstantiate it
        self.tile = self.cover.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.list', 'test'))
        self.assertNotIn(obj1, self.tile.results())
        self.assertNotIn(obj2, self.tile.results())
        self.assertIn(obj3, self.tile.results())

        # We edit the tile to give it a title and a 'more...' link.
        data = self.tile.data
        data['tile_title'] = 'My title'
        data['more_link'] = IUUID(obj2)
        data['more_link_text'] = 'Read much more...'
        # Save the new data.
        data_mgr = ITileDataManager(self.tile)
        data_mgr.set(data)

        # tile's data attribute is cached; reinstantiate it
        self.tile = self.cover.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.list', 'test'))
        self.assertEqual(self.tile.tile_title, 'My title')
        self.assertEqual(
            self.tile.more_link,
            {'href': 'http://nohost/plone/my-image',
             'text': 'Read much more...'})

        # finally, we remove it from the list; the tile must be empty again
        self.tile.remove_item(obj3.UID())
        # tile's data attribute is cached; reinstantiate it
        self.tile = self.cover.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.list', 'test'))
        self.assertTrue(self.tile.is_empty())

    def test_populate_with_uids(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())

        # now we add a couple of objects to the list
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        self.tile.populate_with_uids([IUUID(obj1, None), IUUID(obj2, None)])

        # tile's data attribute is cached; reinstantiate it
        self.tile = self.cover.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.list', 'test'))
        self.assertEqual(len(self.tile.results()), 2)
        self.assertIn(obj1, self.tile.results())
        self.assertIn(obj2, self.tile.results())

    def test_render_empty(self):
        msg = 'Please add up to 5 objects to the tile.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_get_image_position(self):
        # we use the private method to skip memoize cache
        self.assertEqual(self.tile._get_image_position(), u'left')
        tile_conf = self.tile.get_tile_configuration()
        tile_conf['image']['position'] = u'right'
        self.tile.set_tile_configuration(tile_conf)
        self.assertEqual(self.tile._get_image_position(), u'right')

    def test_get_title_tag(self):
        # we use the private method to skip memoize cache
        item = self.portal['my-news-item']
        expected = '<h2><a href="http://nohost/plone/my-news-item">Test news item</a></h2>'
        self.assertEqual(self.tile._get_title_tag(item), expected)
        tile_conf = self.tile.get_tile_configuration()
        tile_conf['title']['htmltag'] = u'h1'
        self.tile.set_tile_configuration(tile_conf)
        expected = '<h1><a href="http://nohost/plone/my-news-item">Test news item</a></h1>'
        self.assertEqual(self.tile._get_title_tag(item), expected)
