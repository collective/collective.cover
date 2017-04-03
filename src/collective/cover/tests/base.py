# -*- coding: utf-8 -*-
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.tiles.base import IPersistentCoverTile
from plone import api
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileType
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestTileMixin:

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            self.cover = api.content.create(
                self.portal, 'collective.cover.content', 'c1')

    def test_interface(self):
        self.assertTrue(self.interface.implementedBy(self.klass))
        self.assertTrue(verifyClass(IPersistentCoverTile, self.klass))
        tile = self.klass(None, None)
        self.assertTrue(self.interface.providedBy(tile))
        self.assertTrue(verifyObject(self.interface, tile))

    def test_tile_registration(self):
        tile_type = queryUtility(ITileType, self.tile.__name__)
        self.assertIsNotNone(tile_type)
        self.assertTrue(issubclass(tile_type.schema, IPersistentCoverTile))
        registry = getUtility(IRegistry)
        self.assertIn(self.tile.__name__, registry['plone.app.tiles'])

    def test_default_configuration(self):
        raise NotImplementedError

    def test_accepted_content_types(self):
        raise NotImplementedError

    def test_esi_render(self):
        """Test ESI rendering capable tiles."""
        from plone.tiles.interfaces import ESI_HEADER_KEY
        from zope.component import queryMultiAdapter
        self.request.environ[ESI_HEADER_KEY] = 'true'
        # tile supports ESI
        from plone.tiles.interfaces import IESIRendered
        IESIRendered.providedBy(self.tile)
        # head and body helper views are available
        head = queryMultiAdapter((self.tile, self.request), name='esi-head')
        self.assertIsNotNone(head)
        body = queryMultiAdapter((self.tile, self.request), name='esi-body')
        self.assertIsNotNone(body)
