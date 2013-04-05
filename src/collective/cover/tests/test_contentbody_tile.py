# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.contentbody import ContentBodyTile
from collective.cover.tiles.base import IPersistentCoverTile
from zope.component import getMultiAdapter
from collective.cover.tiles.permissions import ITilesPermissions
from zope.annotation.interfaces import IAnnotations
from collective.cover.tiles.configuration import ITilesConfigurationScreen


class ContentBodyTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.portal.restrictedTraverse(
            '@@%s/%s' % ('collective.cover.contentbody', 'test-body-tile'))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(ContentBodyTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, ContentBodyTile))

        tile = ContentBodyTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertFalse(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(
            self.tile.accepted_ct(),
            ['Document', 'News Item'])

    def test_empty_body(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        self.assertFalse(self.tile.body())

    def test_body(self):
        text = '<h2>Peace of mind</h2>'
        obj = self.portal['my-news-item']
        obj.setText(text)
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.body(), text)

    def test_render_empty(self):
        self.assertIn(
            "Please drag&amp;drop some content here to populate the tile.",
            self.tile())

    def test_render(self):
        text = '<h2>Peace of mind</h2>'
        obj = self.portal['my-news-item']
        obj.setText(text)

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        # the body need to bring our motto
        self.assertIn('Peace of mind', rendered)

    def test_delete_tile_persistent_data(self):
        permissions = getMultiAdapter(
            (self.tile.context, self.request, self.tile), ITilesPermissions)
        permissions.set_allowed_edit('masters_of_the_universe')
        annotations = IAnnotations(self.tile.context)
        self.assertIn('plone.tiles.permission.test-body-tile', annotations)

        configuration = getMultiAdapter(
            (self.tile.context, self.request, self.tile),
            ITilesConfigurationScreen)
        configuration.set_configuration({
            'uuid': 'c1d2e3f4g5jrw',
        })
        self.assertIn('plone.tiles.configuration.test-body-tile',
                      annotations)

        # Call the delete method
        self.tile.delete()

        # Now we should not see the stored data anymore
        self.assertNotIn('plone.tiles.permission.test-body-tile',
                         annotations)
        self.assertNotIn('plone.tiles.configuration.test-body-tile',
                         annotations)
