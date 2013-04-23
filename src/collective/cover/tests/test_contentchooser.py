# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from zope.component import getMultiAdapter

import json
import re
import unittest


class ContentChooserTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    # XXX: can we get rid of this?
    def test_render(self):
        rendered = self.portal.restrictedTraverse('@@test-content-contentchooser')()
        html = """<a data-ct-type="Document" class="contenttype-document state-missing-value" rel="1">"""
        self.assertRegexpMatches(rendered, re.compile(html))

    def test_jsonbytype(self):
        catalog = self.portal['portal_catalog']
        results = catalog()
        portal_objects_ids = [i.id for i in results]

        view = self.portal.restrictedTraverse('@@jsonbytype')
        json_response = json.loads(view(False, '', ''))
        self.assertIn('parent_url', json_response)
        self.assertIn('path', json_response)
        self.assertIn('items', json_response)
        json_objects_ids = [i['id'] for i in json_response['items']]

        self.assertItemsEqual(json_objects_ids, portal_objects_ids)

    def test_searches(self):
        self.request.set('q', 'Image')
        view = getMultiAdapter(
            (self.portal, self.request), name=u'content-search')
        html = """<a data-ct-type="Document" class="contenttype-document state-missing-value" rel="1">"""
        self.assertFalse(re.compile(html).search(view()))
        html = """<a data-ct-type="Image" class="contenttype-image state-missing-value" rel="1">"""
        self.assertTrue(re.compile(html).search(view()))
