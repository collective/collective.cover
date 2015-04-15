# -*- coding: utf-8 -*-

from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.widgets.selectpreview import SelectPreviewWidget
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import json
import unittest


class WidgetPreviewCase(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_layout_structure(self):
        portal = self.portal
        ttool = api.portal.get_tool('portal_types')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        fti = ttool.getTypeInfo('Document')
        obj = fti.constructInstance(portal, 'test1')

        widget = SelectPreviewWidget(self.portal.REQUEST)
        widget.context = obj
        widget.id = 'test'

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        layouts = settings.layouts
        sl = []

        widget.simplify_layout(json.loads(layouts['Layout A']), sl)

        simplified_layout = [{'type': 'row', 'children': [{'type': 'group', 'children': [{'tile-type': u'collective.cover.carousel', 'type': 'tile'}], 'size': 16}]}, {'type': 'row', 'children': [{'type': 'group', 'children': [{'tile-type': u'collective.cover.list', 'type': 'tile'}], 'size': 8}, {'type': 'group', 'children': [{'tile-type': u'collective.cover.collection', 'type': 'tile'}], 'size': 8}]}, {'type': 'row', 'children': [{'type': 'group', 'children': [{'tile-type': u'collective.cover.basic', 'type': 'tile'}], 'size': 5}, {'type': 'group', 'children': [{'tile-type': u'collective.cover.basic', 'type': 'tile'}], 'size': 5}, {'type': 'group', 'children': [{'tile-type': u'collective.cover.basic', 'type': 'tile'}], 'size': 5}]}]

        self.assertEqual(sl, simplified_layout)
