# -*- coding: utf-8 -*-
from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.carousel import CarouselTile
from collective.cover.tiles.carousel import ICarouselTile
from collective.cover.tiles.carousel import UUIDSFieldDataConverter
from collective.cover.widgets.textlinessortable import TextLinesSortableWidget
from plone import api
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID

import unittest


zptlogo = (
    'GIF89a\x10\x00\x10\x00\xd5\x00\x00\xff\xff\xff\xff\xff\xfe\xfc\xfd\xfd'
    '\xfa\xfb\xfc\xf7\xf9\xfa\xf5\xf8\xf9\xf3\xf6\xf8\xf2\xf5\xf7\xf0\xf4\xf6'
    '\xeb\xf1\xf3\xe5\xed\xef\xde\xe8\xeb\xdc\xe6\xea\xd9\xe4\xe8\xd7\xe2\xe6'
    '\xd2\xdf\xe3\xd0\xdd\xe3\xcd\xdc\xe1\xcb\xda\xdf\xc9\xd9\xdf\xc8\xd8\xdd'
    '\xc6\xd7\xdc\xc4\xd6\xdc\xc3\xd4\xda\xc2\xd3\xd9\xc1\xd3\xd9\xc0\xd2\xd9'
    '\xbd\xd1\xd8\xbd\xd0\xd7\xbc\xcf\xd7\xbb\xcf\xd6\xbb\xce\xd5\xb9\xcd\xd4'
    '\xb6\xcc\xd4\xb6\xcb\xd3\xb5\xcb\xd2\xb4\xca\xd1\xb2\xc8\xd0\xb1\xc7\xd0'
    '\xb0\xc7\xcf\xaf\xc6\xce\xae\xc4\xce\xad\xc4\xcd\xab\xc3\xcc\xa9\xc2\xcb'
    '\xa8\xc1\xca\xa6\xc0\xc9\xa4\xbe\xc8\xa2\xbd\xc7\xa0\xbb\xc5\x9e\xba\xc4'
    '\x9b\xbf\xcc\x98\xb6\xc1\x8d\xae\xbaFgs\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06z@\x80pH,\x12k\xc8$\xd2f\x04'
    '\xd4\x84\x01\x01\xe1\xf0d\x16\x9f\x80A\x01\x91\xc0ZmL\xb0\xcd\x00V\xd4'
    '\xc4a\x87z\xed\xb0-\x1a\xb3\xb8\x95\xbdf8\x1e\x11\xca,MoC$\x15\x18{'
    '\x006}m\x13\x16\x1a\x1f\x83\x85}6\x17\x1b $\x83\x00\x86\x19\x1d!%)\x8c'
    '\x866#\'+.\x8ca`\x1c`(,/1\x94B5\x19\x1e"&*-024\xacNq\xba\xbb\xb8h\xbeb'
    '\x00A\x00;'
)


class CarouselTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(CarouselTileTestCase, self).setUp()
        self.tile = CarouselTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.carousel'
        self.tile.id = u'test'

    def _update_tile_data(self):
        # tile's data attribute is cached; reinstantiate it
        self.tile = self.cover.restrictedTraverse(
            '@@{0}/{1}'.format(str(self.tile.__name__), str(self.tile.id)))

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

    def test_autoplay(self):
        # autoplay is True when tile is empty
        self.assertTrue(self.tile.autoplay())
        # but Galleria init code is not rendered
        self.assertNotIn('options.autoplay = true', self.tile())
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)
        self.assertIn('options.autoplay = true', self.tile())
        data_mgr = ITileDataManager(self.tile)
        data = data_mgr.get()
        data['autoplay'] = False
        data_mgr.set(data)
        self._update_tile_data()
        self.assertFalse(self.tile.autoplay())
        self.assertIn('options.autoplay = false', self.tile())

    def test_crud(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())

        # now we add a couple of objects to the list
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']

        self.tile.populate_with_object(obj1)
        self.tile.populate_with_object(obj2)

        self._update_tile_data()

        # Document should not have been added
        self.assertEqual(len(self.tile.results()), 1)
        self.assertNotIn(obj1, self.tile.results())
        self.assertIn(obj2, self.tile.results())

        # next, we replace the list of objects with a different one
        obj3 = self.portal['my-image1']
        self.tile.replace_with_uuids([IUUID(obj3, None)])
        self._update_tile_data()
        self.assertNotIn(obj1, self.tile.results())
        self.assertNotIn(obj2, self.tile.results())
        self.assertIn(obj3, self.tile.results())

        # finally, we remove it from the list; the tile must be empty again
        self.tile.remove_item(obj3.UID())
        self._update_tile_data()
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

        self.assertTrue(isinstance(uuids, dict))
        self.assertTrue(len(uuids) == 1)
        self.assertTrue(uuids[obj1.UID()]['order'] == u'0')

        # now we add a second image
        obj2 = self.portal['my-image1']

        self.tile.populate_with_object(obj2)

        uuids = ITileDataManager(self.tile).get().get('uuids', None)

        self.assertTrue(isinstance(uuids, dict))
        self.assertTrue(len(uuids) == 2)
        self.assertTrue(uuids[obj1.UID()]['order'] == u'0')
        self.assertTrue(uuids[obj2.UID()]['order'] == u'1')

    def test_custom_title(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())
        uuids = ITileDataManager(self.tile).get().get('uuids', None)

        self.assertIsNone(uuids)

        # now we 2 elements
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']

        self.tile.populate_with_uuids([
            obj1.UID(), obj2.UID()
        ])

        # For obj2 we will assign a custom_title

        uuids = ITileDataManager(self.tile).get().get('uuids', None)
        uuids[obj2.UID()]['custom_title'] = u'New Title'

        title1 = self.tile.get_title(obj1)
        title2 = self.tile.get_title(obj2)

        # Document object should be the same as Title
        self.assertEqual(title1, obj1.Title())
        # First image should return the custom Title
        self.assertEqual(title2, u'New Title')

    def test_custom_description(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())
        uuids = ITileDataManager(self.tile).get().get('uuids', None)

        self.assertIsNone(uuids)

        # now we 2 elements
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']

        self.tile.populate_with_uuids([
            obj1.UID(), obj2.UID()
        ])

        # For obj2 we will assign a custom_description

        uuids = ITileDataManager(self.tile).get().get('uuids', None)
        uuids[obj2.UID()]['custom_description'] = u'New Description'

        description1 = self.tile.get_description(obj1)
        description2 = self.tile.get_description(obj2)

        # Document object should be the same as Description
        self.assertEqual(description1, obj1.Description())
        # First image should return the custom URL
        self.assertEqual(description2, u'New Description')

    def test_custom_url(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())
        uuids = ITileDataManager(self.tile).get().get('uuids', None)

        self.assertIsNone(uuids)

        # now we 3 elements
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        obj3 = self.portal['my-image1']

        self.tile.populate_with_uuids([
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

    def test_get_alt(self):
        obj1 = self.portal['my-image']
        self.tile.populate_with_object(obj1)
        rendered = self.tile()
        # the image is there and the alt attribute is set
        self.assertIn('<img ', rendered)
        self.assertIn(
            'alt="This image was created for testing purposes"', rendered)

    def test_populate_collection(self):
        with api.env.adopt_roles(['Manager']):
            api.content.create(
                self.portal, 'News Item', id='new1', image=zptlogo)
            api.content.create(
                self.portal, 'News Item', id='new2', image=zptlogo)
            api.content.create(
                self.portal, 'News Item', id='new3')
            query = [dict(
                i='portal_type',
                o='plone.app.querystring.operation.selection.is',
                v='News Item',
            )]
            col = api.content.create(
                self.portal, 'Collection', 'collection', query=query)
            api.content.transition(col, 'publish')
        self.tile.populate_with_object(col)
        rendered = self.tile()
        self.assertIn(u'<img src="http://nohost/plone/new1', rendered)
        self.assertIn(u'<img src="http://nohost/plone/new2', rendered)
        self.assertNotIn(u'<img src="http://nohost/plone/new3', rendered)
