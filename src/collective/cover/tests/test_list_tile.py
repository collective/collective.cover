# -*- coding: utf-8 -*-
from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.list import IListTile
from collective.cover.tiles.list import ListTile
from collective.cover.interfaces import ISearchableText
from zope.component import queryAdapter
from DateTime import DateTime
from mock import Mock
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import TEST_USER_NAME
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

    def test_results(self):
        # set standard workflow for News Items
        wt = self.portal['portal_workflow']
        wt.setChainForPortalTypes(['News Item'], 'simple_publication_workflow')
        # create some testing content and add it to the tile
        with api.env.adopt_roles(['Manager']):
            folder = api.content.create(self.portal, 'Folder', id='test')
        for i in range(1, 10):
            obj = api.content.create(folder, 'News Item', id=str(i))
            self.tile.populate_with_object(obj)

        # tile should list the first 5 objects
        results = self.tile.results()
        self.assertEqual(len(results), 5)
        for i in range(1, 6):
            self.assertIn(folder[str(i)], results)

        # for an anonymous user, no content is returned
        logout()
        results = self.tile.results()
        self.assertEqual(len(results), 0)

        # for the test user, the first 5 objects should be still there
        login(self.portal, TEST_USER_NAME)
        results = self.tile.results()
        self.assertEqual(len(results), 5)
        for i in range(1, 6):
            self.assertIn(folder[str(i)], results)

        # delete one object; it should be removed from the tile also
        api.content.delete(folder['1'])
        results = self.tile.results()
        self.assertEqual(len(results), 5)
        for i in range(2, 7):
            self.assertIn(folder[str(i)], results)

    def test_show_start_date_on_events(self):
        from DateTime import DateTime
        tomorrow = DateTime() + 1
        # create an Event starting tomorrow
        with api.env.adopt_roles(['Manager']):
            event = api.content.create(
                self.portal, 'Event', 'event', startDate=tomorrow)
            api.content.transition(event, 'publish')

        self.tile.populate_with_object(event)
        rendered = self.tile()
        tomorrow = api.portal.get_localized_time(tomorrow, long_format=True)
        self.assertIn(tomorrow, rendered)

    def test_localized_time_is_rendered(self):
        tomorrow = DateTime() + 1
        # create an Event starting tomorrow
        with api.env.adopt_roles(['Manager']):
            event = api.content.create(
                self.portal, 'Event', 'event', startDate=tomorrow)
            api.content.transition(event, 'publish')

        self.tile.populate_with_object(event)
        rendered = self.tile()
        expected = api.portal.get_localized_time(
            tomorrow, long_format=True, time_only=False)
        self.assertIn(expected, rendered)  # u'Jul 15, 2015 01:23 PM'

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['title']['format'] = 'dateonly'
        self.tile.set_tile_configuration(tile_conf)
        rendered = self.tile()
        expected = api.portal.get_localized_time(
            tomorrow, long_format=False, time_only=False)
        self.assertIn(expected, rendered)  # u'Jul 15, 2015

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['title']['format'] = 'timeonly'
        self.tile.set_tile_configuration(tile_conf)
        rendered = self.tile()
        expected = api.portal.get_localized_time(
            tomorrow, long_format=False, time_only=True)
        self.assertIn(expected, rendered)  # u'01:23 PM'

    def test_seachable_text(self):
        searchable = queryAdapter(self.tile, ISearchableText)
        self.tile.data['tile_title'] = 'custom title'
        self.tile.data['more_link_text'] = 'custom more link text'
        self.assertEqual(searchable.SearchableText(), 'custom title custom more link text')
