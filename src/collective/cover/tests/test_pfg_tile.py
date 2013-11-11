# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.configuration import ITilesConfigurationScreen
from collective.cover.tiles.permissions import ITilesPermissions
from collective.cover.tiles.pfg import PFGTile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class PFGTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUpUser(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Editor', 'Reviewer'])
        login(self.portal, TEST_USER_NAME)

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.setUpUser()
        self.portal.invokeFactory('FormFolder',
                                  id='my-form',
                                  title='My Form',
                                  description='A form form FormGen')
        self.pfg = self.portal['my-form']
        self.tile = self.portal.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.pfg', 'test-pfg-tile'))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(PFGTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, PFGTile))

        tile = PFGTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

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
        self.assertIn(
            'Please drag&amp;drop a Form Folder here to populate the tile.',
            self.tile())

    def test_render(self):
        obj = self.pfg

        self.tile.populate_with_object(obj)
        rendered = self.tile()

        self.assertIn('Your E-Mail Address', rendered)

    def test_render_deleted_object(self):
        obj = self.pfg

        self.tile.populate_with_object(obj)
        # Delete original object
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.manage_delObjects(['my-form', ])
        rendered = self.tile()

        self.assertIn('Please drag&amp;drop', rendered)

    def test_render_restricted_object(self):
        obj = self.pfg

        self.tile.populate_with_object(obj)
        obj.manage_permission('View', [], 0)
        rendered = self.tile()

        self.assertIn('Please drag&amp;drop', rendered)

    def test_delete_tile_persistent_data(self):
        permissions = getMultiAdapter(
            (self.tile.context, self.request, self.tile), ITilesPermissions)
        permissions.set_allowed_edit('masters_of_the_universe')
        annotations = IAnnotations(self.tile.context)
        self.assertIn('plone.tiles.permission.test-pfg-tile', annotations)

        uuid = IUUID(self.pfg, None)
        configuration = getMultiAdapter(
            (self.tile.context, self.request, self.tile),
            ITilesConfigurationScreen)
        configuration.set_configuration({
            'uuid': uuid,
            'title': self.pfg.Title(),
            'description': self.pfg.Description(),
        })
        self.assertIn('plone.tiles.configuration.test-pfg-tile',
                      annotations)

        # Call the delete method
        self.tile.delete()

        # Now we should not see the stored data anymore
        self.assertNotIn('plone.tiles.permission.test-pfg-tile',
                         annotations)
        self.assertNotIn('plone.tiles.configuration.test-pfg-tile',
                         annotations)
