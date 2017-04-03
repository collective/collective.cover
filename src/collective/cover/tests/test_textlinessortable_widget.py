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

    def test_get_custom_title(self):
        widget = TextLinesSortableWidget(self.request)

        obj1 = self.portal['my-image']
        obj2 = self.portal['my-image1']
        obj3 = self.portal['my-image2']

        widget.context = {'uuids': {
            obj1.UID(): {u'order': u'0', u'custom_title': u'custom_title'},
            obj2.UID(): {u'order': u'1', u'custom_title': u''},
            obj3.UID(): {u'order': u'2'},
        }
        }

        self.assertEqual(
            widget.get_custom_title(obj1.UID()),
            u'custom_title'
        )
        self.assertEqual(
            widget.get_custom_title(obj2.UID()),
            u'Test image #1'
        )
        self.assertEqual(
            widget.get_custom_title(obj3.UID()),
            u'Test image #2'
        )

    def test_get_custom_description(self):
        widget = TextLinesSortableWidget(self.request)

        obj1 = self.portal['my-image']
        obj2 = self.portal['my-image1']
        obj3 = self.portal['my-image2']

        widget.context = {'uuids': {
            obj1.UID(): {u'order': u'0', u'custom_description': u'custom_description'},
            obj2.UID(): {u'order': u'1', u'custom_description': u''},
            obj3.UID(): {u'order': u'2'},
        }
        }

        self.assertEqual(
            widget.get_custom_description(obj1.UID()),
            u'custom_description'
        )
        self.assertEqual(
            widget.get_custom_description(obj2.UID()),
            u'This image #1 was created for testing purposes'
        )
        self.assertEqual(
            widget.get_custom_description(obj3.UID()),
            u'This image #2 was created for testing purposes'
        )

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
        self.assertEqual(widget.get_custom_url(obj2.UID()), u'http://nohost/plone/my-image1/view')
        self.assertEqual(widget.get_custom_url(obj3.UID()), u'http://nohost/plone/my-image2/view')

    def test_extract(self):
        obj1 = self.portal['my-image']
        obj2 = self.portal['my-image1']
        obj3 = self.portal['my-image2']
        uuids = [
            obj1.UID(),
            obj3.UID(),
            obj2.UID()
        ]

        name = 'uuid.field'
        self.request.set(name, u'\r\n'.join(uuids))
        self.request.set(u'{0}.custom_url.{1}'.format(name, obj1.UID()), u'custom_url')
        self.request.set(u'{0}.custom_url.{1}'.format(name, obj2.UID()), u'')

        widget = TextLinesSortableWidget(self.request)
        widget.name = name

        expected = {
            obj1.UID(): {
                u'custom_url': u'custom_url',
                u'order': u'0'
            },
            obj2.UID(): {u'order': u'2'},
            obj3.UID(): {u'order': u'1'}
        }

        extracted_value = widget.extract()

        self.assertDictEqual(extracted_value, expected)

        # Test with weird line separators \n\n in IE11 for the uuids
        self.request.set(name, u'\n\n'.join(uuids))

        extracted_value = widget.extract()
        self.assertDictEqual(extracted_value, expected)

    def test_utf8_custom_data(self):
        obj = self.portal['my-image']
        obj.setDescription('áéíóú')

        name = 'uuid.field'
        self.request.set(name, u'{0}'.format(obj.UID()))
        self.request.set(u'{0}.custom_description.{1}'.format(name, obj.UID()), u'áéíóú')

        widget = TextLinesSortableWidget(self.request)
        widget.name = name

        expected = {
            obj.UID(): {u'order': u'0'},
        }

        extracted_value = widget.extract()

        self.assertDictEqual(extracted_value, expected)
