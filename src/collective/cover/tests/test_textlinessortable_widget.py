# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.widgets.textlinessortable import TextLinesSortableWidget

import unittest


class TestTextLinesSortableWidget(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_sort_results(self):
        widget = TextLinesSortableWidget(self.request)

        obj1 = self.portal['my-image']
        obj2 = self.portal['my-image1']
        obj3 = self.portal['my-image2']

        widget.context = {'uuids': {
            obj1.UID(): {u'order': u'0'},
            obj2.UID(): {u'order': u'2'},
            obj3.UID(): {u'order': u'1'},
        }
        }

        expected = [
            {'obj': obj1, 'uuid': obj1.UID()},
            {'obj': obj3, 'uuid': obj3.UID()},
            {'obj': obj2, 'uuid': obj2.UID()},
        ]
        self.assertListEqual(widget.sort_results(), expected)

        widget.context = {'uuids': {}}

        expected = []
        self.assertListEqual(widget.sort_results(), expected)

    def test_thumbnail(self):
        widget = TextLinesSortableWidget(self.request)

        obj1 = self.portal['my-image']
        obj2 = self.portal['my-document']

        self.assertIsNotNone(widget.thumbnail(obj1))
        self.assertIsNone(widget.thumbnail(obj2))

    def test_get_custom_url(self):
        widget = TextLinesSortableWidget(self.request)

        obj1 = self.portal['my-image']
        obj2 = self.portal['my-image1']
        obj3 = self.portal['my-image2']

        widget.context = {'uuids': {
            obj1.UID(): {u'order': u'0', u'custom_url': u'custom_url'},
            obj2.UID(): {u'order': u'1', u'custom_url': u''},
            obj3.UID(): {u'order': u'2'},
        }
        }

        self.assertEqual(widget.get_custom_url(obj1.UID()), u'custom_url')
        self.assertEqual(widget.get_custom_url(obj2.UID()), u'')
        self.assertEqual(widget.get_custom_url(obj3.UID()), u'')

    def test_extract(self):
        name = 'uuid.field'
        self.request.set(name, u'uuid1\r\nuuid3\r\nuuid2')
        self.request.set(u'%s.custom_url.uuid1' % name, u'custom_url')
        self.request.set(u'%s.custom_url.uuid2' % name, u'')

        widget = TextLinesSortableWidget(self.request)
        widget.name = name

        expected = {
            u'uuid1': {u'order': u'0', u'custom_url': u'custom_url'},
            u'uuid3': {u'order': u'1', u'custom_url': u''},
            u'uuid2': {u'order': u'2', u'custom_url': u''},
        }

        extracted_value = widget.extract()

        self.assertDictEqual(extracted_value, expected)
