# -*- coding: utf-8 -*-

from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from cStringIO import StringIO
from plone.tiles.interfaces import IPersistentTile
from plone.tiles.interfaces import ITileDataManager
from zope.component import eventtesting
from zope.configuration.xmlconfig import xmlconfig
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest

ZCML = """
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:five="http://namespaces.zope.org/five"
    xmlns:plone="http://namespaces.plone.org/plone">

  <include package="zope.component" file="meta.zcml" />
  <include package="Products.Five" />
  <five:loadProducts file="meta.zcml"/>
  <include package="plone.tiles" />
  <include package="plone.tiles" file="meta.zcml"/>

  <plone:tile
      name="collective.cover.base"
      title="the base tile"
      description="the mother of all tiles."
      add_permission="cmf.ModifyPortalContent"
      schema="collective.cover.tiles.base.IPersistentCoverTile"
      class="collective.cover.tiles.base.PersistentCoverTile"
      permission="zope2.View"
      for="*"
      />

</configure>
"""


class BaseTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def _register_tile(self):
        xmlconfig(StringIO(ZCML))

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        eventtesting.setUp()

        self._register_tile()
        self.tile = PersistentCoverTile(self.portal, self.request)
        # XXX: tile initialization
        self.tile.__name__ = 'collective.cover.base'

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(PersistentCoverTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, PersistentCoverTile))
        # cover tiles inherit from plone.tile PersistentTile
        self.assertTrue(IPersistentTile.implementedBy(PersistentCoverTile))

        tile = PersistentCoverTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))
        # cover tiles inherit from plone.tile PersistentTile
        self.assertTrue(IPersistentTile.providedBy(tile))
        #self.assertTrue(verifyObject(IPersistentTile, tile))

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ALL_CONTENT_TYPES)

    def test_delete_tile_persistent_data(self):
        eventtesting.clearEvents()
        # First, let's assign an id to the tile and store some data
        self.tile.id = 'test-tile'
        data_mgr = ITileDataManager(self.tile)
        data_mgr.set({'test': 'data'})

        # We see that the data persists
        self.assertIn('test', data_mgr.get())
        self.assertEqual(data_mgr.get()['test'], 'data')

        # Call the delete method
        self.tile.delete()

        # Now we should not see the stored data anymore
        self.assertNotIn('test', data_mgr.get())

        events = eventtesting.getEvents()

        # Finally, test that ObjectModifiedEvent was fired for the cover
        self.assertEqual(events[0].object, self.portal)
