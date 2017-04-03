# -*- coding: utf-8 -*-
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.configuration import ITilesConfigurationScreen
from collective.cover.tiles.permissions import ITilesPermissions
from collective.cover.tiles.pfg import IPFGTile
from collective.cover.tiles.pfg import PFGTile
from mock import Mock
from plone import api
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter

import unittest


class PFGTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(PFGTileTestCase, self).setUp()
        self.tile = PFGTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.pfg'
        self.tile.id = u'test'

        with api.env.adopt_roles(['Manager']):
            self.pfg = api.content.create(
                self.portal,
                'FormFolder',
                id='my-form',
                title='My Form',
                description='A form form FormGen',
            )

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = IPFGTile
        self.klass = PFGTile
        super(PFGTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ['FormFolder'])

    def test_empty_body(self):
        self.assertFalse(self.tile.body())

    def test_body(self):
        obj = self.pfg
        self.tile.populate_with_object(obj)
        self.assertIn('<label class="formQuestion" for="replyto">',
                      self.tile.body())

    def test_render_empty(self):
        msg = 'Please drag&amp;drop a Form Folder here to populate the tile.'

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn(msg, self.tile())

        self.tile.is_compose_mode = Mock(return_value=False)
        self.assertNotIn(msg, self.tile())

    def test_render(self):
        obj = self.pfg

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        self.assertIn('Your E-Mail Address', rendered)

    def test_render_deleted_object(self):
        obj = self.pfg

        self.tile.populate_with_object(obj)
        # Delete original object
        self.portal.manage_delObjects(['my-form'])

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn('Please drag&amp;drop', self.tile())

    def test_render_restricted_object(self):
        obj = self.pfg

        self.tile.populate_with_object(obj)
        obj.manage_permission('View', [], 0)

        self.tile.is_compose_mode = Mock(return_value=True)
        self.assertIn('Please drag&amp;drop', self.tile())

    def test_delete_tile_persistent_data(self):
        permissions = getMultiAdapter(
            (self.tile.context, self.request, self.tile), ITilesPermissions)
        permissions.set_allowed_edit('masters_of_the_universe')
        annotations = IAnnotations(self.tile.context)
        self.assertIn('plone.tiles.permission.test', annotations)

        uuid = IUUID(self.pfg, None)
        configuration = getMultiAdapter(
            (self.tile.context, self.request, self.tile),
            ITilesConfigurationScreen)
        configuration.set_configuration({
            'uuid': uuid,
            'title': self.pfg.Title(),
            'description': self.pfg.Description(),
        })
        self.assertIn('plone.tiles.configuration.test', annotations)

        # Call the delete method
        self.tile.delete()

        # Now we should not see the stored data anymore
        self.assertNotIn('plone.tiles.permission.test', annotations)
        self.assertNotIn('plone.tiles.configuration.test', annotations)


def test_suite():
    # XXX: load tests only in Plone < 5
    from collective.cover.testing import HAS_PFG
    from collective.cover.config import IS_PLONE_5
    if HAS_PFG and not IS_PLONE_5:
        return unittest.defaultTestLoader.loadTestsFromName(__name__)
    else:
        return unittest.TestSuite()
