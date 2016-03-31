# -*- coding: utf-8 -*-

from collective.cover.config import PLONE_VERSION
from collective.cover.testing import INTEGRATION_TESTING
from lxml import etree
from plone import api
from StringIO import StringIO

import json
import unittest


parser = etree.HTMLParser()


class ContentChooserTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    # XXX: can we get rid of this?
    def test_render(self):
        rendered = self.portal.restrictedTraverse('@@test-content-contentchooser')()
        tree = etree.parse(StringIO(rendered), parser)
        document_match = tree.xpath("//li[@data-content-type='Document']/a[@class='contenttype-document state-missing-value'][contains(@title, 'This document was created for testing purposes')][contains(@title, '/my-document')][@rel='1']")
        self.assertTrue(document_match)

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
        view = api.content.get_view(u'content-search', self.portal, self.request)
        tree = etree.parse(StringIO(view()), parser)
        document_match = tree.xpath("//li[@data-content-type='Document']/a[@class='contenttype-document state-missing-value'][contains(@title, 'This document was created for testing purposes')][contains(@title, '/my-document')][@rel='1']")
        self.assertFalse(document_match)
        image_match = tree.xpath("//li[@data-content-type='Image']/a[@class='contenttype-image state-missing-value'][contains(@title, 'This image #2 was created for testing purposes')][contains(@title, '/my-image')][@rel='1']")
        self.assertTrue(image_match)

    @unittest.skipIf(
        PLONE_VERSION < '4.3',
        'On Plone 4.2 we need to install Products.UnicodeLexicon')
    def test_unicode_aware_lexicon(self):
        """See: https://github.com/collective/collective.cover/issues/276
        """
        view = api.content.get_view(u'content-search', self.portal, self.request)
        self.portal['my-document'].setTitle(
            u'A crise do apagão foi uma crise nacional ocorrida no Brasil, '
            u'que afetou o fornecimento e distribuição de energia elétrica.')
        self.portal['my-document'].reindexObject()
        results = view.search(query=u'apagao')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].getPath(), '/plone/my-document')
        results = view.search(query=u'apagão')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].getPath(), '/plone/my-document')

    def test_asian_lang_searches(self):
        """See: https://github.com/collective/collective.cover/issues/374
        """
        view = api.content.get_view(u'content-search', self.portal, self.request)
        self.portal['my-document'].setTitle(
            u'日本語のコンテンツを追加します。, '
            u'検索にかかるように設定します。')
        self.portal['my-document'].reindexObject()
        results = view.search(query=u'日本語')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].getPath(), '/plone/my-document')
        results = view.search(query=u'検索')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].getPath(), '/plone/my-document')

    def test_batch_searches(self):
        self.request.set('q', 'Image')
        view = api.content.get_view(u'content-search', self.portal, self.request)
        batch = view.search(query=None, page=1, b_size=1)
        # It's a batch and respect the size
        self.assertEqual(len(list(batch)), 1)

    def test_update(self):
        # We are just testing against issue 383: next-page link in contentchooser
        view = api.content.get_view(u'content-search', self.portal, self.request)
        self.request.set('page', 1)
        self.request.set('b_size', 1)
        view.update()
        self.assertEqual(view.nextpage, 2)
