# -*- coding: utf-8 -*-
from collective.cover.testing import INTEGRATION_TESTING
from plone import api

import unittest


class CoverAPITestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def _create_cover(self, id, layout):
        with api.env.adopt_roles(['Manager']):
            return api.content.create(
                self.portal, 'collective.cover.content',
                id,
                template_layout=layout,
            )

    def setUp(self):
        self.portal = self.layer['portal']

    def test_get_tiles(self):
        cover = self._create_cover('c1', 'Empty layout')
        self.assertEqual(len(cover.get_tiles()), 0)
        cover = self._create_cover('c2', 'Layout A')
        self.assertEqual(len(cover.get_tiles()), 6)
        types = u'collective.cover.carousel'
        self.assertEqual(len(cover.get_tiles(types)), 1)
        types = [u'collective.cover.carousel', u'collective.cover.basic']
        self.assertEqual(len(cover.get_tiles(types)), 4)

    def test_list_tiles(self):
        cover = self._create_cover('c1', 'Empty layout')
        self.assertEqual(len(cover.list_tiles()), 0)
        cover = self._create_cover('c2', 'Layout A')
        self.assertEqual(len(cover.list_tiles()), 6)
        types = u'collective.cover.carousel'
        self.assertEqual(len(cover.list_tiles(types)), 1)
        types = [u'collective.cover.carousel', u'collective.cover.basic']
        self.assertEqual(len(cover.list_tiles(types)), 4)

    def test_get_tile_type(self):
        cover = self._create_cover('c1', 'Empty layout')
        with self.assertRaises(ValueError):
            cover.get_tile_type('invalid_id')

        cover = self._create_cover('c2', 'Layout A')
        tiles = cover.get_tiles()
        for t in tiles:
            self.assertEqual(t['type'], cover.get_tile_type(t['id']))

    def test_get_tile(self):
        from plone.tiles import PersistentTile
        cover = self._create_cover('c2', 'Layout A')
        tiles = cover.list_tiles()
        for t in tiles:
            self.assertTrue(isinstance(cover.get_tile(t), PersistentTile))

    def test_set_tile_data(self):
        cover = self._create_cover('c2', 'Layout A')
        tiles = cover.list_tiles()
        title = u'Törkylempijävongahdus'
        description = u"Wieniläinen sioux'ta puhuva ökyzombie diggaa Åsan roquefort-tacoja."
        data = dict(title=title, description=description)
        cover.set_tile_data(tiles[3], **data)  # fourth tile is a Basic one
        tile = cover.get_tile(tiles[3])
        self.assertEqual(tile.data['title'], title)
        self.assertEqual(tile.data['description'], description)

    def test_get_referenced_objects(self):
        cover = self._create_cover('c2', 'Layout A')
        self.assertEqual(cover.get_referenced_objects(), set([]))
        image = self.portal['my-image']
        tiles = cover.list_tiles()
        for tile_uuid in tiles:
            tile = cover.get_tile(tile_uuid)
            tile.populate_with_object(image)
        self.assertEqual(cover.get_referenced_objects(), set([image]))
        link = self.portal['my-link']
        for tile_uuid in tiles:
            tile = cover.get_tile(tile_uuid)
            tile.populate_with_object(link)
        self.assertEqual(cover.get_referenced_objects(), set([image, link]))
