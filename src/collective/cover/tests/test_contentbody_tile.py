# -*- coding: utf-8 -*-
from collective.cover.tests.base import TestTileMixin
from collective.cover.tests.utils import set_text_field
from collective.cover.tiles.configuration import ITilesConfigurationScreen
from collective.cover.tiles.contentbody import ContentBodyTile
from collective.cover.tiles.contentbody import IContentBodyTile
from collective.cover.tiles.permissions import ITilesPermissions
from mock import Mock
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter

import unittest


class ContentBodyTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(ContentBodyTileTestCase, self).setUp()
        self.tile = ContentBodyTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.contentbody'
        self.tile.id = u'test'

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IContentBodyTile
        self.klass = ContentBodyTile
        super(ContentBodyTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertFalse(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['Document', 'News Item'])

    def test_is_empty(self):
        self.assertTrue(self.tile.is_empty)

    def test_empty_body(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        self.assertFalse(self.tile.body())

    def test_body(self):
        text = '<h2>Peace of mind</h2>'
        obj = self.portal['my-news-item']
        set_text_field(obj, text)  # handle Archetypes and Dexterity
        self.tile.populate_with_object(obj)
        self.assertEqual(self.tile.body(), text)

    def test_render_empty(self):
        msg = 'Drag&amp;drop some content to populate the tile.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_render(self):
        text = '<h2>Peace of mind</h2>'
        obj = self.portal['my-news-item']
        set_text_field(obj, text)  # handle Archetypes and Dexterity

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        # the body need to bring our motto
        self.assertIn('Peace of mind', rendered)

    def test_render_deleted_object(self):
        text = '<h2>Peace of mind</h2>'
        obj = self.portal['my-news-item']
        set_text_field(obj, text)  # handle Archetypes and Dexterity

        self.tile.populate_with_object(obj)
        # Delete original object
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.manage_delObjects(['my-news-item', ])

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(
            'This item does not have any body text.',
            self.tile()
        )

    def test_render_restricted_object(self):
        text = '<h2>Peace of mind</h2>'
        obj = self.portal['my-news-item']
        set_text_field(obj, text)  # handle Archetypes and Dexterity

        self.tile.populate_with_object(obj)
        obj.manage_permission('View', [], 0)

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(
            'This item does not have any body text.',
            self.tile()
        )

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
            'uuid': 'c1d2e3f4g5jrw',
        })
        self.assertIn('plone.tiles.configuration.test', annotations)

        # Call the delete method
        self.tile.delete()

        # Now we should not see the stored data anymore
        self.assertNotIn('plone.tiles.permission.test', annotations)
        self.assertNotIn('plone.tiles.configuration.test', annotations)

    def test_item_url(self):
        obj = self.portal['my-news-item']

        self.tile.populate_with_object(obj)
        url = self.tile.item_url()
        self.assertEqual(url, obj.absolute_url())
