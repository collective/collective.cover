# -*- coding: utf-8 -*-

from collective.cover.config import PROJECTNAME
from collective.cover.testing import INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class TilesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    # FIXME: remove tiles on uninstall
    @unittest.expectedFailure
    def test_tiles_removed_on_uninstall(self):
        qi = self.portal['portal_quickinstaller']
        qi.uninstallProducts(products=[PROJECTNAME])
        tiles = self.registry['plone.app.tiles']
        self.assertTrue(u'collective.cover.basic' not in tiles)
        self.assertTrue(u'collective.cover.carousel' not in tiles)
        self.assertTrue(u'collective.cover.collection' not in tiles)
        self.assertTrue(u'collective.cover.embed' not in tiles)
        self.assertTrue(u'collective.cover.file' not in tiles)
        self.assertTrue(u'collective.cover.list' not in tiles)
        self.assertTrue(u'collective.cover.richtext' not in tiles)


class PageLayoutTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.name = u"collective.cover.carousel"
        self.cover = self.portal['frontpage']
        self.tile = getMultiAdapter((self.cover, self.request), name=self.name)
        self.tile = self.tile['test']
        self.view = self.cover.unrestrictedTraverse("@@layout")

    def test_is_droppable(self):
        self.assertTrue(self.view.tile_is_droppable('collective.cover.basic'))

    def test_is_editable(self):
        self.assertTrue(self.view.tile_is_editable('collective.cover.basic'))

    def test_is_configurable(self):
        self.assertTrue(self.view.tile_is_configurable(
            'collective.cover.basic')
        )
