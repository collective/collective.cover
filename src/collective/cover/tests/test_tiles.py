# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry

from collective.cover.config import PROJECTNAME
from collective.cover.testing import INTEGRATION_TESTING


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
        self.assertTrue(u'collective.cover.link' not in tiles)
        self.assertTrue(u'collective.cover.list' not in tiles)
        self.assertTrue(u'collective.cover.richtext' not in tiles)
