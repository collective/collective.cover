# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from plone.dexterity.utils import createContentInContainer
from zope.component import queryMultiAdapter

import unittest


class LayoutTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.cover = createContentInContainer(
            self.portal, 'collective.cover.content', checkConstraints=False)

    def test_uid_getter(self):
        view = queryMultiAdapter((self.cover, self.request), name='uid_getter')
        self.assertIsNotNone(view)

        # this tests our UUID don't start with a number
        # see: https://github.com/collective/collective.cover/issues/137
        # let's generate a bunch of UUID; 16 should be enough
        for i in range(16):
            uuid = view()
            self.assertFalse(uuid[0].isdigit())
