# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry

from collective.composition.config import PROJECTNAME
from collective.composition.testing import INTEGRATION_TESTING


class TilesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_tiles_removed_on_uninstall(self):
        qi = self.portal['portal_quickinstaller']
        qi.uninstallProducts(products=[PROJECTNAME])
        tiles = self.registry['plone.app.tiles']
        self.assertTrue(u'collective.composition.basic' not in tiles)
        self.assertTrue(u'collective.composition.collection' not in tiles)
        self.assertTrue(u'collective.composition.file' not in tiles)
        self.assertTrue(u'collective.composition.richtext' not in tiles)
