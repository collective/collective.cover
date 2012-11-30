# -*- coding: utf-8 -*-

import unittest2 as unittest
import re

from collective.cover.testing import INTEGRATION_TESTING


class LinkTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_render(self):
        rendered = self.portal.restrictedTraverse('@@test-content-screenlet')()
        html = """<a data-ct-type="Document" class="contenttype-document state-missing-value" rel="1">"""
        self.assertRegexpMatches(rendered, re.compile(html))
