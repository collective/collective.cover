# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from plone import api

import unittest


class LayoutTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'folder')

        self.cover = api.content.create(
            self.folder, 'collective.cover.content', 'cover')

    def test_uid_getter(self):
        """Test our UUID do not start with a number.

        See: https://github.com/collective/collective.cover/issues/137
        """
        view = api.content.get_view(u'uid_getter', self.cover, self.request)

        # let's generate a bunch of UUID; 16 should be enough
        for i in range(16):
            uuid = view()
            self.assertFalse(uuid[0].isdigit())
