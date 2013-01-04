# -*- coding: utf-8 -*-

import unittest2 as unittest

from DateTime import DateTime

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
from zope.component import getMultiAdapter

from collective.cover.testing import INTEGRATION_TESTING, loadImage
from collective.cover.tiles.basic import BasicTile
from collective.cover.tiles.base import IPersistentCoverTile


class ContentTreeTabPathTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.layer['portal'].restrictedTraverse('@@%s/%s' %
                                                            ('collective.cover.basic',
                                                             'test-basic-tile',))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(BasicTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, BasicTile))

        tile = BasicTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(),
                         ['Collection', 'Document', 'File',
                          'Image', 'Link', 'News Item'])

    def test_empty_date(self):
        self.assertEqual(None, self.tile.Date())

    def test_populated_empty_date(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        self.assertEqual(obj.Date(), self.tile.Date())

    def test_populated_date(self):
        obj = self.portal['my-news-item']
        obj.effective_date = DateTime()
        self.tile.populate_with_object(obj)
        self.assertEqual(obj.Date(), self.tile.Date())

    def test_populated_faultydate(self):
        obj = self.portal['my-news-item']
        obj.effective_date = DateTime('1/1/1800')
        self.tile.populate_with_object(obj)
        self.assertEqual(obj.Date(), self.tile.Date())

    def test_populate_with_object(self):
        self.tile.populate_with_object(self.portal['my-news-item'])
        self.assertEqual('Test news item', self.tile.data['title'])
        self.assertEqual('This news item was created for testing purposes',
                         self.tile.data['description'])

    def test_render_empty(self):
        self.assertTrue('Please drag&amp;drop some content here to '
                        'populate the tile.' in self.tile())

    def test_render_title(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertTrue('Test news item' in rendered)

    def test_render(self):
        obj = self.portal['my-news-item']
        obj.setSubject('test-subject')
        obj.effective_date = DateTime()
        obj.setImage(loadImage('canoneye.jpg'))
        obj.reindexObject()

        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertTrue(obj.absolute_url() in rendered)
        self.assertTrue('Test news item' in rendered)
        self.assertTrue('This news item was created for testing purposes'
                        in rendered)
        self.assertTrue('test-subject' in rendered)
        # the localized time must be there
        utils = getMultiAdapter((self.portal, self.request), name=u'plone')
        date = utils.toLocalizedTime(obj.Date(), True)
        self.assertTrue(date in rendered)
        self.assertTrue('test-basic-tile/@@images' in rendered)
