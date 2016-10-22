# -*- coding: utf-8 -*-
from collective.cover.tests.base import TestTileMixin
from collective.cover.tests.utils import today
from collective.cover.tiles.collection import CollectionTile
from collective.cover.tiles.collection import ICollectionTile
from mock import Mock
from plone import api
from plone.uuid.interfaces import IUUID

import unittest


EMPTY = [dict(
    i='portal_type',
    o='plone.app.querystring.operation.selection.is',
    v='Foo',
)]

EVENTS = [dict(
    i='portal_type',
    o='plone.app.querystring.operation.selection.is',
    v='Event',
)]


class CollectionTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(CollectionTileTestCase, self).setUp()
        self.tile = CollectionTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.collection'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = ICollectionTile
        self.klass = CollectionTile
        super(CollectionTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['Collection'])

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_populate_tile_with_object_unicode(self):
        """We must store unicode always on schema.TextLine and schema.Text
        fields to avoid UnicodeDecodeError.
        """
        title = u'El veloz murciélago hindú comía feliz cardillo y kiwi'
        obj = self.portal['mandelbrot-set']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.data.get('header'), title)
        self.assertTrue(self.tile.data.get('footer'))
        self.assertEqual(self.tile.data.get('uuid'), IUUID(obj))
        self.assertIsInstance(self.tile.data.get('header'), unicode)
        self.assertIsInstance(self.tile.data.get('footer'), unicode)

    def test_populate_tile_with_object_string(self):
        """This test complements test_populate_with_object_unicode
        using strings instead of unicode objects.
        """
        title = 'The quick brown fox jumps over the lazy dog'
        obj = self.portal['mandelbrot-set']
        obj.setTitle(title)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(unicode(title, 'utf-8'), self.tile.data.get('header'))
        self.assertTrue(self.tile.data.get('footer'))
        self.assertEqual(self.tile.data.get('uuid'), IUUID(obj))

    def test_populate_tile_with_invalid_object(self):
        obj = self.portal['my-document']
        self.tile.populate_with_object(obj)
        self.assertTrue(self.tile.is_empty())

    def test_render_empty_collection(self):
        obj = self.portal['mandelbrot-set']
        obj.setQuery(EMPTY)
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn("The collection doesn't have any results.", rendered)

    def test_render_deleted_collection(self):
        obj = self.portal['mandelbrot-set']
        self.tile.populate_with_object(obj)

        with api.env.adopt_roles(['Manager']):
            self.portal.manage_delObjects(['mandelbrot-set'])

        msg = 'Please drop a collection here to fill the tile.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_thumbnail(self):
        # as a File does not have an image field, we should have no thumbnail
        obj = self.portal['my-file']
        self.assertFalse(self.tile.thumbnail(obj))

        # as an Image does have an image field, we should have a thumbnail
        obj = self.portal['my-image']
        thumbnail = self.tile.thumbnail(obj)
        self.assertIsNotNone(thumbnail)

    def test_thumbnail_not_visible(self):
        # turn visibility off, we should have no thumbnail
        # XXX: refactor; we need a method to easily change field visibility
        tile_conf = self.tile.get_tile_configuration()
        tile_conf['image']['visibility'] = u'off'
        self.tile.set_tile_configuration(tile_conf)
        assert not self.tile._field_is_visible('image')
        obj = self.portal['my-image']
        self.assertIsNone(self.tile.thumbnail(obj))

    def test_thumbnail_original_image(self):
        # use original image instead of a thumbnail
        tile_conf = self.tile.get_tile_configuration()
        tile_conf['image']['imgsize'] = '_original'
        self.tile.set_tile_configuration(tile_conf)
        obj = self.portal['my-image']
        self.assertTrue(self.tile.thumbnail(obj))
        self.assertIsInstance(self.tile(), unicode)

    def test_number_of_items(self):
        obj = self.portal['mandelbrot-set']
        self.tile.populate_with_object(obj)

        # Collection has three images and shows them all.
        self.assertEqual(len(self.tile.results()), 3)

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['number_to_show']['size'] = 2
        self.tile.set_tile_configuration(tile_conf)

        # Collection has three images and shows the first two items.
        items = self.tile.results()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].getId(), 'my-image')
        self.assertEqual(items[1].getId(), 'my-image1')

    def test_offset(self):
        obj = self.portal['mandelbrot-set']
        self.tile.populate_with_object(obj)

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['offset']['offset'] = 1
        self.tile.set_tile_configuration(tile_conf)

        # Collection has three images and shows the final two.
        items = self.tile.results()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].getId(), 'my-image1')
        self.assertEqual(items[1].getId(), 'my-image2')

        # Add a size, so only one item is left.
        tile_conf['number_to_show']['size'] = 1
        self.tile.set_tile_configuration(tile_conf)

        items = self.tile.results()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].getId(), 'my-image1')

    def test_random_items(self):
        obj = self.portal['mandelbrot-set']
        self.tile.populate_with_object(obj)

        # we need to compare lists of objects
        ordered = [o for o in obj.results()]
        results = [o for o in self.tile.results()]
        # default behavior return results in order
        self.assertEqual(results, ordered)

        # now, return results in random order
        self.tile.data['random'] = True
        for i in range(0, 10):
            results = [o for o in self.tile.results()]
            if results != ordered:
                return

        self.fail('No random order after 10 attemps')

    def _create_events_collection(self):
        with api.env.adopt_roles(['Manager']):
            obj = api.content.create(
                self.portal, 'Collection', 'collection', query=EVENTS)
            api.content.transition(obj, 'publish')
            assert len(obj.results()) == 1
        return obj

    def test_show_start_date_on_events(self):
        obj = self._create_events_collection()
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        start_date = api.portal.get_localized_time(today, long_format=True)
        self.assertIn(start_date, rendered)

    def test_date_on_items(self):
        collection = self.portal['mandelbrot-set']
        self.tile.populate_with_object(collection)

        tile_config = self.tile.get_tile_configuration()
        self.assertEqual(tile_config['date']['visibility'], u'on')

        # Get the first news item from the collection
        content_listing_obj = collection.results()[0]

        date = self.tile.Date(content_listing_obj)
        self.assertFalse(callable(date), 'Date should not be calleable')

        fmt_date = self.portal.toLocalizedTime(date, True)

        rendered = self.tile()
        self.assertTrue(
            fmt_date in rendered,
            'Formatted date should be in rendered tile'
        )

    def test_localized_time_is_rendered(self):
        obj = self._create_events_collection()
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        expected = api.portal.get_localized_time(
            today, long_format=True, time_only=False)
        self.assertIn(expected, rendered)  # u'Jul 15, 2015 01:23 PM'

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['date']['format'] = 'dateonly'
        self.tile.set_tile_configuration(tile_conf)
        rendered = self.tile()
        expected = api.portal.get_localized_time(
            today, long_format=False, time_only=False)
        self.assertIn(expected, rendered)  # u'Jul 15, 2015

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['date']['format'] = 'timeonly'
        self.tile.set_tile_configuration(tile_conf)
        rendered = self.tile()
        expected = api.portal.get_localized_time(
            today, long_format=False, time_only=True)
        self.assertIn(expected, rendered)  # u'01:23 PM'

    def test_get_alt(self):
        obj = self.portal['mandelbrot-set']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        # the image is there and the alt attribute is set
        self.assertIn('<img ', rendered)
        self.assertIn(
            'alt="This image was created for testing purposes"', rendered)
