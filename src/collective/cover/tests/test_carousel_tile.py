# -*- coding: utf-8 -*-
from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.carousel import CarouselTile
from collective.cover.tiles.carousel import ICarouselTile
from collective.cover.tiles.carousel import UUIDSFieldDataConverter
from collective.cover.widgets.textlinessortable import TextLinesSortableWidget
from persistent.mapping import PersistentMapping
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID

import unittest


class CarouselTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(CarouselTileTestCase, self).setUp()
        self.tile = CarouselTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.carousel'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = ICarouselTile
        self.klass = CarouselTile
        super(CarouselTileTestCase, self).test_interface()

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
            '@@{0}/{1}'.format('collective.cover.carousel', 'test'))

        # Document should not have been added
        self.assertEqual(len(self.tile.results()), 1)
        self.assertNotIn(obj1, self.tile.results())
        self.assertIn(obj2, self.tile.results())

        # next, we replace the list of objects with a different one
        obj3 = self.portal['my-image1']
        self.tile.replace_with_objects([IUUID(obj3, None)])
        # tile's data attribute is cached; reinstantiate it
        self.tile = self.cover.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.carousel', 'test'))
        self.assertNotIn(obj1, self.tile.results())
        self.assertNotIn(obj2, self.tile.results())
        self.assertIn(obj3, self.tile.results())

        # finally, we remove it from the list; the tile must be empty again
        self.tile.remove_item(obj3.UID())
        # tile's data attribute is cached; reinstantiate it
        self.tile = self.cover.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.carousel', 'test'))
        self.assertTrue(self.tile.is_empty())

    def test_internal_structure(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())
        uuids = ITileDataManager(self.tile).get().get('uuids', None)

        self.assertIsNone(uuids)

        # now we add an image
        obj1 = self.portal['my-image']

        self.tile.populate_with_object(obj1)

        uuids = ITileDataManager(self.tile).get().get('uuids', None)

        self.assertTrue(isinstance(uuids, PersistentMapping))
        self.assertTrue(len(uuids) == 1)
        self.assertTrue(uuids[obj1.UID()]['order'] == u'0')

        # now we add a second image
        obj2 = self.portal['my-image1']

        self.tile.populate_with_object(obj2)

        uuids = ITileDataManager(self.tile).get().get('uuids', None)

        self.assertTrue(isinstance(uuids, PersistentMapping))
        self.assertTrue(len(uuids) == 2)
        self.assertTrue(uuids[obj1.UID()]['order'] == u'0')
        self.assertTrue(uuids[obj2.UID()]['order'] == u'1')

    def test_custom_url(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())
        uuids = ITileDataManager(self.tile).get().get('uuids', None)

        self.assertIsNone(uuids)

        # now we 3 elements
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        obj3 = self.portal['my-image1']

        self.tile.populate_with_uids([
            obj1.UID(), obj2.UID(), obj3.UID()
        ])

        # For obj2 we will assign a custom_url

        uuids = ITileDataManager(self.tile).get().get('uuids', None)
        uuids[obj2.UID()]['custom_url'] = u'http://www.custom_url.com'

        url1 = self.tile.get_url(obj1)
        url2 = self.tile.get_url(obj2)
        url3 = self.tile.get_url(obj3)

        # Document object should be the same as absolute_url
        self.assertEqual(url1, obj1.absolute_url())
        # First image should return the custom URL
        self.assertEqual(url2, u'http://www.custom_url.com')
        # And second image should have the absolute_url and /view
        self.assertEqual(url3, u'%s/view' % obj3.absolute_url())

    def test_data_converter(self):
        field = ICarouselTile['uuids']
        widget = TextLinesSortableWidget(self.request)
        conv = UUIDSFieldDataConverter(field, widget)

        value = {
            u'uuid1': {u'order': u'0'},
            u'uuid2': {u'order': u'2'},
            u'uuid3': {u'order': u'1'},
        }

        to_widget = conv.toWidgetValue(value)
        self.assertEqual(to_widget, u'uuid1\r\nuuid3\r\nuuid2')

        to_field = conv.toFieldValue(value)

        self.assertEqual(to_field, value)
        self.assertEqual(conv.toFieldValue({}), conv.field.missing_value)
