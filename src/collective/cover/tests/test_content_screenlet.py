# -*- coding: utf-8 -*-

import unittest2 as unittest
import re

from collective.cover.testing import INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
try:
    import json
    json = json  # Pyflakes
except ImportError:
    import simplejson as json


class LinkTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_render(self):
        rendered = self.portal.restrictedTraverse('@@test-content-screenlet')()
        html = """<a data-ct-type="Document" class="contenttype-document state-missing-value" rel="1">"""
        self.assertRegexpMatches(rendered, re.compile(html))

    def test_jsonbytype(self):
        portal_objects_ids = [i.id for i in
                              getToolByName(self.portal, 'portal_catalog')()]
        view = self.portal.restrictedTraverse('@@jsonbytype')
        json_response = json.loads(view(False, '', ''))
        self.assertIn('parent_url', json_response)
        self.assertIn('path', json_response)
        self.assertIn('items', json_response)
        json_objects_ids = [i['id'] for i in json_response['items']]
        self.assertItemsEqual(json_objects_ids, portal_objects_ids)

    def test_searches(self):
        self.request.set('q', 'Image')
        view = getMultiAdapter((self.portal, self.request),
                               name=u'content-search')
        html = """<a data-ct-type="Document" class="contenttype-document state-missing-value" rel="1">"""
        self.assertFalse(re.compile(html).search(view()))
        html = """<a data-ct-type="Image" class="contenttype-image state-missing-value" rel="1">"""
        self.assertTrue(re.compile(html).search(view()))
