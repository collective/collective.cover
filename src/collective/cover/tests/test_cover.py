# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from collective.cover.config import DEFAULT_GRID_SYSTEM
from collective.cover.controlpanel import ICoverSettings
from collective.cover.interfaces import ICover
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.lockingbehavior.behaviors import ILocking
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from zope.component import createObject
from zope.component import getUtility
from zope.component import queryUtility

import json
import unittest


class CoverIntegrationTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'folder')

        self.cover = api.content.create(
            self.folder, 'collective.cover.content', 'c1')

    def test_adding(self):
        self.assertTrue(ICover.providedBy(self.cover))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        self.assertIsNotNone(fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        schema = fti.lookupSchema()
        self.assertEqual(ICover, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ICover.providedBy(new_object))

    def test_exclude_from_navigation_behavior(self):
        self.assertTrue(IExcludeFromNavigation.providedBy(self.cover))

    def test_locking_behavior(self):
        self.assertTrue(ILocking.providedBy(self.cover))

    def test_cover_selectable_as_folder_default_view(self):
        self.folder.setDefaultPage('c1')
        self.assertEqual(self.folder.getDefaultPage(), 'c1')

    def test_export_permission(self):
        # layout export is visible for user with administrative rights
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        layout_edit = self.cover.restrictedTraverse('layoutedit')
        self.assertTrue(layout_edit.can_export_layout())
        self.assertIn('<span>Export layout</span>', layout_edit())

        # Accessing layoutedit as simple Member is not allowed.
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        with self.assertRaises(Unauthorized):
            self.cover.restrictedTraverse('layoutedit')

        # But we can cheat a bit here by reusing the layout_edit
        # object that has been visited as a Manager above.  The
        # layout export should still not be visible for this user.
        self.assertFalse(layout_edit.can_export_layout())
        self.assertNotIn('<span>Export layout</span>', layout_edit())

    # TODO: move this to a browser view test
    def test_layoutmanager_settings(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        layout_edit = self.cover.restrictedTraverse('layoutedit')
        settings = json.loads(layout_edit.layoutmanager_settings())
        if DEFAULT_GRID_SYSTEM == 'deco16_grid':
            self.assertEqual(settings, {'ncolumns': 16})
        elif DEFAULT_GRID_SYSTEM == 'bootstrap3':
            self.assertEqual(settings, {'ncolumns': 12})

        # Choose different grid.
        registry = getUtility(IRegistry)
        cover_settings = registry.forInterface(ICoverSettings)
        if DEFAULT_GRID_SYSTEM == 'deco16_grid':
            cover_settings.grid_system = 'bootstrap3'

            # The number of columns should be different now.
            settings = json.loads(layout_edit.layoutmanager_settings())
            self.assertEqual(settings, {'ncolumns': 12})
        elif DEFAULT_GRID_SYSTEM == 'bootstrap3':
            cover_settings.grid_system = 'deco16_grid'

            # The number of columns should be different now.
            settings = json.loads(layout_edit.layoutmanager_settings())
            self.assertEqual(settings, {'ncolumns': 16})

        # Choose different grid.
        registry = getUtility(IRegistry)
        cover_settings = registry.forInterface(ICoverSettings)
        cover_settings.grid_system = 'bootstrap2'

        # The number of columns should be different now.
        settings = json.loads(layout_edit.layoutmanager_settings())
        self.assertEqual(settings, {'ncolumns': 12})

    def test_searchabletext_indexer(self):
        from collective.cover.content import searchableText
        from plone.app.textfield.value import RichTextValue
        from plone.tiles.interfaces import ITileDataManager
        self.cover.title = u'Lorem ipsum'
        self.cover.description = u'Neque porro'
        # set up a simple layout with a two RichText tiles
        self.cover.cover_layout = u"""
            [{"children":
                [{"children": [
                    {"class": "tile",
                     "id": "test1",
                     "tile-type": "collective.cover.richtext",
                     "type": "tile"},
                    {"class": "tile",
                     "id": "test2",
                     "tile-type": "collective.cover.richtext",
                     "type": "tile"}],
                "column-size": 8,
                "id": "group1",
                "roles": ["Manager"],
                "type": "group"}],
            "class": "row",
            "type": "row"}]
            """
        tile = self.cover.restrictedTraverse('collective.cover.richtext/test1')
        value1 = RichTextValue(
            raw=u'<p>01234</p>',
            mimeType='text/x-html-safe',
            outputMimeType='text/x-html-safe')
        data_mgr = ITileDataManager(tile)
        data_mgr.set({'text': value1})
        tile = self.cover.restrictedTraverse('collective.cover.richtext/test2')
        data_mgr = ITileDataManager(tile)
        value2 = RichTextValue(
            raw=u'<p>56789</p>',
            mimeType='text/x-html-safe',
            outputMimeType='text/x-html-safe')
        data_mgr.set({'text': value2})

        # indexer should contain id, title, description and text in tiles
        self.assertEqual(
            searchableText(self.cover)(),
            u'c1 Lorem ipsum Neque porro 01234 56789'
        )

    # TODO: add test for plone.app.relationfield.behavior.IRelatedItems
