# -*- coding: utf-8 -*-
from collective.cover.testing import ALL_CONTENT_TYPES
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from cStringIO import StringIO
from plone.tiles.interfaces import ITileDataManager
from zope.component import eventtesting
from zope.configuration.xmlconfig import xmlconfig

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


class BaseTileTestCase(TestTileMixin, unittest.TestCase):

    def _register_tile(self):
        xmlconfig(StringIO(ZCML))

    def setUp(self):
        super(BaseTileTestCase, self).setUp()
        eventtesting.setUp()
        self._register_tile()
        self.tile = PersistentCoverTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.base'
        self.tile.id = u'test'

    def test_interface(self):
        self.interface = IPersistentCoverTile
        self.klass = PersistentCoverTile
        super(BaseTileTestCase, self).test_interface()

    def test_tile_registration(self):
        pass

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), ALL_CONTENT_TYPES)

    def test_delete_tile_persistent_data(self):
        eventtesting.clearEvents()
        # First, let's store some data on the tile
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
        self.assertEqual(events[0].object, self.cover)
