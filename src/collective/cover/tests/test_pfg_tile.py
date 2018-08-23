# -*- coding: utf-8 -*-
"""Test for the PloneFormGen tile.

They run only if Products.PloneFormGen is installed.

XXX: PFG tile is deprecated and will be removed in collective.cover 3
"""
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.pfg import IPFGTile
from collective.cover.tiles.pfg import PFGTile
from mock import Mock
from plone import api

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


def test_suite():
    """Run tests only if Products.PloneFormGen is installed."""
    from collective.cover.testing import HAS_PFG
    if HAS_PFG:
        return unittest.defaultTestLoader.loadTestsFromName(__name__)
    else:
        return unittest.TestSuite()
