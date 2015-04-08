# -*- coding: utf-8 -*-
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.config import PLONE_VERSION
from plone import api
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

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
        self.request.set('b_size', 100)
        rendered = self.portal.restrictedTraverse('@@test-content-contentchooser')()
        html = 'title="document:/plone/my-document"'
        self.assertIn(html, rendered)

    def test_jsonbytype(self):
        catalog = self.portal['portal_catalog']
        types = queryUtility(
            IVocabularyFactory,
            name=u'plone.app.vocabularies.ReallyUserFriendlyTypes'
        )(self.portal)
        results = catalog(
            portal_type=[t.value for t in types],
            path={'query': '/'.join(self.portal.getPhysicalPath()),
                  'depth': 1}
        )
        portal_objects_ids = [i.id for i in results]

        view = self.portal.restrictedTraverse('@@jsonbytype')
        json_response = json.loads(view(False, '', ''))
        self.assertIn('parent_url', json_response)
        self.assertIn('path', json_response)
        self.assertIn('items', json_response)
        json_objects_ids = [i['id'] for i in json_response['items']]

        self.assertItemsEqual(json_objects_ids, portal_objects_ids)

    def test_searches(self):
        self.request.set('b_size', 100)
        self.request.set('q', 'Image')
        view = api.content.get_view(u'content-search', self.portal,
                                    self.request)
        html = 'title="document:/plone/my-document"'
        self.assertNotIn(html, view())
        html = 'title="image:/plone/my-image2"'
        self.assertIn(html, view())

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
