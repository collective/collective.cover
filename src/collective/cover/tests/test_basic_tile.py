# -*- coding: utf-8 -*-
from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.tests.base import TestTileMixin
from collective.cover.tests.utils import today
from collective.cover.tiles.basic import BasicTile
from collective.cover.tiles.basic import IBasicTile
from collective.cover.tiles.configuration import ITilesConfigurationScreen
from collective.cover.tiles.permissions import ITilesPermissions
from DateTime import DateTime
from mock import Mock
from plone import api
from plone.app.testing import logout
from plone.cachepurging.hooks import queuePurge
from plone.cachepurging.interfaces import ICachePurgingSettings
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.component import provideUtility
from zope.component import queryUtility
from zope.component.globalregistry import provideHandler
from zope.globalrequest import setRequest
from zope.interface import alsoProvides

import unittest


class BasicTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(BasicTileTestCase, self).setUp()
        self.tile = BasicTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.basic'
        self.tile.id = u'test'

    @property
    def get_tile(self):
        """Return a new instance of the tile to avoid data caching."""
        return self.cover.restrictedTraverse(
            '@@{0}/{1}'.format(self.tile.__name__, self.tile.id))

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IBasicTile
        self.klass = BasicTile
        super(BasicTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ALL_CONTENT_TYPES)

    def test_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_populated(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        self.assertFalse(self.tile.is_empty())

    def test_populated_with_private_content(self):
        with api.env.adopt_roles(['Manager']):
            obj = api.content.create(self.portal, 'Collection', 'foo')
        self.tile.populate_with_object(obj)
        self.assertFalse(self.tile.is_empty())

        # tile must be empty for anonymous user
        logout()
        tile = self.get_tile  # avoid data caching on tile
        self.assertTrue(tile.is_empty())

    def test_manually_populated(self):
        # simulate user populating tile by editing it (no drag-and-drop)
        data = dict(title='foo')
        data_mgr = ITileDataManager(self.tile)
        data_mgr.set(data)
        self.assertFalse(self.tile.is_empty())

        # tile must not be empty for anonymous user
        logout()
        tile = self.get_tile  # avoid data caching on tile
        self.assertFalse(tile.is_empty())

    def test_date_on_empty_tile(self):
        self.assertIsNone(self.tile.Date())

    def test_date_on_populated_tile(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        self.assertEqual(obj.Date(), self.tile.Date())

    def test_populate_with_object(self):
        self.tile.populate_with_object(self.portal['my-news-item'])
        self.assertEqual('Test news item', self.tile.data['title'])
        self.assertEqual('This news item was created for testing purposes',
                         self.tile.data['description'])

    def test_populate_with_object_unicode(self):
        """We must store unicode always on schema.TextLine and schema.Text
        fields to avoid UnicodeDecodeError.
        """
        title = u'παν γράμμα'
        description = u'El veloz murciélago hindú comía feliz cardillo y kiwi'
        obj = self.portal['my-news-item']
        obj.setTitle(title)
        obj.setDescription(description)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(title, self.tile.data['title'])
        self.assertEqual(description, self.tile.data['description'])
        self.assertIsInstance(self.tile.data.get('title'), unicode)
        self.assertIsInstance(self.tile.data.get('description'), unicode)

    def test_populate_with_object_string(self):
        """This test complements test_populate_with_object_unicode
        using strings instead of unicode objects.
        """
        title = 'Pangram'
        description = 'The quick brown fox jumps over the lazy dog'
        obj = self.portal['my-news-item']
        obj.setTitle(title)
        obj.setDescription(description)
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        self.assertEqual(
            unicode(title, 'utf-8'),
            self.tile.data.get('title')
        )
        self.assertEqual(
            unicode(description, 'utf-8'),
            self.tile.data.get('description')
        )

    def test_render_empty(self):
        msg = 'Please drag&amp;drop some content here to populate the tile.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_render_deleted_object(self):
        # We will use an image to test it
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)

        # image is shown normally
        rendered = self.tile()
        self.assertIn('@@images', rendered)

        with api.env.adopt_roles(['Manager']):
            api.content.delete(obj)

        tile = self.get_tile  # avoid data caching on tile
        rendered = tile()

        # image should still be shown since it was copied to the tile
        self.assertIn('@@images', rendered)

    def test_render(self):
        obj = self.portal['my-news-item']
        obj.setSubject(['subject1', 'subject2'])
        obj.effective_date = DateTime()
        obj.reindexObject()

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        # the title and a link to the original object must be there
        self.assertIn('Test news item', rendered)
        self.assertIn(obj.absolute_url(), rendered)

        # the description must be there
        self.assertIn(
            '<p>This news item was created for testing purposes</p>', rendered)

        # the localized time must be there
        date = api.portal.get_localized_time(obj.Date(), long_format=True)
        self.assertIn(date, rendered)

        # the tags must be there
        self.assertIn('subject1', rendered)
        self.assertIn('subject2', rendered)

        # the image is there and the alt attribute is set
        self.assertIn('<img ', rendered)
        self.assertIn('alt="This news item was created for testing purposes"', rendered)

    def test_delete_tile_persistent_data(self):
        permissions = getMultiAdapter(
            (self.tile.context, self.request, self.tile), ITilesPermissions)
        permissions.set_allowed_edit('masters_of_the_universe')
        annotations = IAnnotations(self.tile.context)
        self.assertIn('plone.tiles.permission.test', annotations)

        configuration = getMultiAdapter(
            (self.tile.context, self.request, self.tile),
            ITilesConfigurationScreen)
        configuration.set_configuration({
            'title': {'order': u'0', 'visibility': u'on'},
            'description': {'order': u'1', 'visibility': u'off'},
        })
        self.assertIn('plone.tiles.configuration.test', annotations)

        # Call the delete method
        self.tile.delete()

        # Now we should not see the stored data anymore
        self.assertNotIn('plone.tiles.permission.test', annotations)
        self.assertNotIn('plone.tiles.configuration.test', annotations)

    def test_populate_with_file(self):
        obj = self.portal['my-file']
        obj.setSubject(['subject1', 'subject2'])
        obj.effective_date = DateTime()
        obj.reindexObject()

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        # there is no image...
        self.assertNotIn('test/@@images', rendered)

    def test_basic_tile_image(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('test/@@images', rendered)

    def test_double_dragging_content_with_image(self):
        # https://github.com/collective/collective.cover/issues/449
        obj = self.portal['my-image']
        data_mgr = ITileDataManager(self.tile)
        self.tile.populate_with_object(obj)
        self.assertIn('image_mtime', data_mgr.get())
        self.assertTrue(float(data_mgr.get()['image_mtime']))
        # populate tile for second time with same object
        self.tile.populate_with_object(obj)
        self.assertIn('image_mtime', data_mgr.get())
        self.assertTrue(float(data_mgr.get()['image_mtime']))
        # tile is rendered with no issues
        rendered = self.tile()
        self.assertIn('<html xmlns="http://www.w3.org/1999/xhtml">', rendered)

    def test_basic_tile_purge_cache(self):
        provideHandler(queuePurge)

        request = self.request
        alsoProvides(request, IAttributeAnnotatable)
        setRequest(request)

        registry = queryUtility(IRegistry)
        registry.registerInterface(ICachePurgingSettings)
        provideUtility(registry, IRegistry)

        settings = registry.forInterface(ICachePurgingSettings)
        settings.enabled = True
        settings.cachingProxies = ('http://localhost:1234',)

        obj = self.portal['my-image']
        data = self.tile.data
        scales = api.content.get_view(u'images', obj, self.request)
        self.tile.data['image'] = NamedBlobImage(str(scales.scale('image').data))
        data_mgr = ITileDataManager(self.tile)
        data_mgr.set(data)

        self.assertEqual(
            set([
                '/c1/@@collective.cover.basic/test',
                '/c1/@@collective.cover.basic/test/@@images/image',
                '/c1/@@collective.cover.basic/test/@@images/icon',
                '/c1/@@collective.cover.basic/test/@@images/mini',
                '/c1/@@collective.cover.basic/test/@@images/large',
                '/c1/@@collective.cover.basic/test/@@images/listing',
                '/c1/@@collective.cover.basic/test/@@images/thumb',
                '/c1/@@collective.cover.basic/test/@@images/preview',
                '/c1/@@collective.cover.basic/test/@@images/tile']),
            IAnnotations(request)['plone.cachepurging.urls'])

    def test_show_start_date_on_events(self):
        event = self.portal['my-event']
        self.tile.populate_with_object(event)
        rendered = self.tile()
        start_date = api.portal.get_localized_time(today, long_format=True)
        self.assertIn(start_date, rendered)

    def test_localized_time_is_rendered(self):
        event = self.portal['my-event']
        self.tile.populate_with_object(event)
        rendered = self.tile()
        expected = api.portal.get_localized_time(
            today, long_format=True, time_only=False)
        self.assertIn(expected, rendered)  # u'Jul 15, 2015 01:23 PM'

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['title']['format'] = 'dateonly'
        self.tile.set_tile_configuration(tile_conf)
        rendered = self.tile()
        expected = api.portal.get_localized_time(
            today, long_format=False, time_only=False)
        self.assertIn(expected, rendered)  # u'Jul 15, 2015

        tile_conf = self.tile.get_tile_configuration()
        tile_conf['title']['format'] = 'timeonly'
        self.tile.set_tile_configuration(tile_conf)
        rendered = self.tile()
        expected = api.portal.get_localized_time(
            today, long_format=False, time_only=True)
        self.assertIn(expected, rendered)  # u'01:23 PM'

    def test_seachable_text(self):
        from collective.cover.interfaces import ISearchableText
        from zope.component import queryAdapter
        searchable = queryAdapter(self.tile, ISearchableText)
        self.tile.data['title'] = 'custom title'
        self.tile.data['description'] = 'custom description'
        self.assertEqual(searchable.SearchableText(), 'custom title custom description')
