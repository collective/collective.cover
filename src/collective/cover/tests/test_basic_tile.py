# -*- coding: utf-8 -*-

from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.testing import generate_jpeg
from collective.cover.testing import images_are_equal
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.basic import BasicTile
from collective.cover.tiles.configuration import ITilesConfigurationScreen
from collective.cover.tiles.permissions import ITilesPermissions
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.cachepurging.hooks import queuePurge
from plone.cachepurging.interfaces import ICachePurgingSettings
from plone.namedfile.file import NamedBlobImage as NamedImageFile
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.component import provideUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.globalregistry import provideHandler
from zope.globalrequest import setRequest
from zope.interface import alsoProvides
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class BasicTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.portal.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.basic', 'test-basic-tile'))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(BasicTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, BasicTile))

        tile = BasicTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ALL_CONTENT_TYPES)

    def test_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_is_not_empty(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        self.assertFalse(self.tile.is_empty())

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
        self.assertIn(
            'Please drag&amp;drop some content here to populate the tile.',
            self.tile())

    def test_render_title(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('Test news item', rendered)

    def test_render_deleted_object(self):
        # We will use an image to test it
        obj = self.portal['my-image']
        self.tile.populate_with_object(obj)

        # Normally the image will be displayed
        rendered = self.tile()
        self.assertIn('@@images', rendered)

        # Delete original object
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.manage_delObjects(['my-image', ])
        # To avoid caching, we get the tile again
        tile = self.portal.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.basic', 'test-basic-tile'))
        tile.is_empty()
        rendered = tile()
        # Now we gracefully ignore the lack of original image
        self.assertNotIn('@@images', rendered)

    def test_basic_tile_render(self):
        obj = self.portal['my-news-item']
        obj.setSubject(['subject1', 'subject2'])
        obj.effective_date = DateTime()
        obj.setImage(generate_jpeg(128, 128))
        obj.reindexObject()

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        # the title and a link to the original object must be there
        self.assertIn('Test news item', rendered)
        self.assertIn(obj.absolute_url(), rendered)

        # the description must be there
        self.assertIn(
            'This news item was created for testing purposes', rendered)

        # the localized time must be there
        utils = getMultiAdapter((self.portal, self.request), name=u'plone')
        date = utils.toLocalizedTime(obj.Date(), True)
        self.assertIn(date, rendered)

        # the tags must be there
        self.assertIn('subject1', rendered)
        self.assertIn('subject2', rendered)

    def test_alt_atribute_present_in_image(self):
        """Object's title must be displayed in image alt attribute.
        See: https://github.com/collective/collective.cover/issues/182
        """
        obj = self.portal['my-news-item']
        obj.setImage(generate_jpeg(128, 128))
        obj.reindexObject()
        self.tile.populate_with_object(obj)
        tile_conf_adapter = getMultiAdapter((self.tile.context, self.request, self.tile),
                                            ITilesConfigurationScreen)
        tile_conf_adapter.set_configuration({'image': {'visibility': 'on', 'imgsize': 'large'}})
        rendered = self.tile()
        self.assertIn('alt="Test news item"', rendered)

    def test_delete_tile_persistent_data(self):
        permissions = getMultiAdapter(
            (self.tile.context, self.request, self.tile), ITilesPermissions)
        permissions.set_allowed_edit('masters_of_the_universe')
        annotations = IAnnotations(self.tile.context)
        self.assertIn('plone.tiles.permission.test-basic-tile', annotations)

        configuration = getMultiAdapter(
            (self.tile.context, self.request, self.tile),
            ITilesConfigurationScreen)
        configuration.set_configuration({
            'title': {'order': u'0', 'visibility': u'on'},
            'description': {'order': u'1', 'visibility': u'off'},
        })
        self.assertIn('plone.tiles.configuration.test-basic-tile',
                      annotations)

        # Call the delete method
        self.tile.delete()

        # Now we should not see the stored data anymore
        self.assertNotIn('plone.tiles.permission.test-basic-tile',
                         annotations)
        self.assertNotIn('plone.tiles.configuration.test-basic-tile',
                         annotations)

    def test_populate_with_file(self):
        obj = self.portal['my-file']
        obj.setSubject(['subject1', 'subject2'])
        obj.effective_date = DateTime()
        obj.reindexObject()

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        # there is no image...
        self.assertNotIn('test-basic-tile/@@images', rendered)

    def test_image_traverser(self):
        obj = self.portal['my-image']
        data = self.tile.data
        scales = queryMultiAdapter((obj, self.request), name='images')
        self.tile.data['image'] = NamedImageFile(str(scales.scale('image').data))
        data_mgr = ITileDataManager(self.tile)
        data_mgr.set(data)
        scales = self.layer['portal'].restrictedTraverse(
            '@@{0}/{1}/@@images'.format('collective.cover.basic', 'test-basic-tile'))
        img = scales.scale('image')
        self.assertTrue(images_are_equal(str(self.tile.data['image'].data),
                                         str(img.index_html().read())))

    def test_basic_tile_image(self):
        obj = self.portal['my-news-item']
        obj.setImage(generate_jpeg(128, 128))
        obj.reindexObject()

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        # old code copy the image
        self.assertNotIn('test-basic-tile/@@images', rendered)

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
        scales = queryMultiAdapter((obj, self.request), name='images')
        self.tile.data['image'] = NamedImageFile(str(scales.scale('image').data))
        data_mgr = ITileDataManager(self.tile)
        data_mgr.set(data)

        self.assertEqual(
            set([
                '/@@collective.cover.basic/test-basic-tile',
                '/@@collective.cover.basic/test-basic-tile/@@images/image',
                '/@@collective.cover.basic/test-basic-tile/@@images/icon',
                '/@@collective.cover.basic/test-basic-tile/@@images/mini',
                '/@@collective.cover.basic/test-basic-tile/@@images/large',
                '/@@collective.cover.basic/test-basic-tile/@@images/listing',
                '/@@collective.cover.basic/test-basic-tile/@@images/thumb',
                '/@@collective.cover.basic/test-basic-tile/@@images/preview',
                '/@@collective.cover.basic/test-basic-tile/@@images/tile']),
            IAnnotations(request)['plone.cachepurging.urls'])
