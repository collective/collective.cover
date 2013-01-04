# -*- coding: utf-8 -*-

import unittest2 as unittest

from DateTime import DateTime

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from collective.cover.testing import INTEGRATION_TESTING, loadImage
from collective.cover.tiles.basic import BasicTile
from collective.cover.tiles.base import IPersistentCoverTile
from zope.component import getMultiAdapter
from collective.cover.tiles.permissions import ITilesPermissions
from zope.annotation.interfaces import IAnnotations
from collective.cover.tiles.configuration import ITilesConfigurationScreen


class BasicTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.portal.restrictedTraverse(
            '@@%s/%s' % ('collective.cover.basic', 'test-basic-tile'))

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
        self.assertEqual(
            self.tile.accepted_ct(),
            ['Collection', 'Document', 'File', 'Image', 'Link', 'News Item'])

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

    def test_render_empty(self):
        self.assertIn(
            "Please drag&amp;drop some content here to populate the tile.",
            self.tile())

    def test_render_title(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertIn('Test news item', rendered)

    def test_render(self):
        obj = self.portal['my-news-item']
        obj.setSubject(['subject1', 'subject2'])
        obj.effective_date = DateTime()
        obj.setImage(loadImage('canoneye.jpg'))
        obj.reindexObject()

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        # the title and a link to the original object must be there
        self.assertIn('Test news item', rendered)
        self.assertIn(obj.absolute_url(), rendered)

        # the description must be there
        self.assertIn(
            "This news item was created for testing purposes", rendered)

        # the image must be there
        self.assertIn('test-basic-tile/@@images', rendered)

        # the localized time must be there
        utils = getMultiAdapter((self.portal, self.request), name=u'plone')
        date = utils.toLocalizedTime(obj.Date(), True)
        self.assertIn(date, rendered)

        # the tags must be there
        self.assertIn('subject1', rendered)
        self.assertIn('subject2', rendered)

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
