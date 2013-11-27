# -*- coding: utf-8 -*-

from collective.cover.interfaces import IGridSystem
from collective.cover.testing import INTEGRATION_TESTING
from plone.dexterity.utils import createContentInContainer
from zope.component import queryMultiAdapter, getUtility

import copy
import unittest


class LayoutTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.cover = createContentInContainer(
            self.portal, 'collective.cover.content', checkConstraints=False)

    def test_uid_getter(self):
        view = queryMultiAdapter((self.cover, self.request), name='uid_getter')
        self.assertIsNotNone(view)

        # this tests our UUID don't start with a number
        # see: https://github.com/collective/collective.cover/issues/137
        # let's generate a bunch of UUID; 16 should be enough
        for i in range(16):
            uuid = view()
            self.assertFalse(uuid[0].isdigit())


class Deco16GridTestCase(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def test_empty(self):
        """Do-nothing case does nothing"""
        self.assertEqual(self.doTransform([]), [])

    def test_overflow(self):
        """Overflowing row marks items as such"""
        self.assertEqual(
            self.doTransform([{u'type': u'row', 'children': [
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'}},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'}},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'}},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'}},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'}},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'}},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'}},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'}},
            ]}]),
            [{u'type': u'row', 'class': 'row', 'children': [
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'},
                 'class': 'cell width-4 position-0'},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'},
                 'class': 'cell width-4 position-4'},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'},
                 'class': 'cell width-4 position-8'},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'},
                 'class': 'cell width-4 position-12'},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'},
                 'class': 'cell width-4 position-16 overflowing'},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'},
                 'class': 'cell width-4 position-20 overflowing'},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'},
                 'class': 'cell width-4 position-24 overflowing'},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'},
                 'class': 'cell width-4 position-28 overflowing'},
            ]}],
        )

        # Item is half-inside grid is still overflowing
        self.assertEqual(
            self.doTransform([{u'type': u'row', 'children': [
                {u'type': u'group',
                 'data': {u'column-size': 15, u'layout-type': u'column'}},
                {u'type': u'group',
                 'data': {u'column-size': 2, u'layout-type': u'column'}},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'}},
            ]}]),
            [{u'type': u'row', 'class': 'row', 'children': [
                {u'type': u'group',
                 'data': {u'column-size': 15, u'layout-type': u'column'},
                 'class': 'cell width-15 position-0'},
                {u'type': u'group',
                 'data': {u'column-size': 2, u'layout-type': u'column'},
                 'class': 'cell width-2 position-15 overflowing'},
                {u'type': u'group',
                 'data': {u'column-size': 4, u'layout-type': u'column'},
                 'class': 'cell width-4 position-17 overflowing'},
            ]}],
        )

        # Items that are too big are too big
        self.assertEqual(
            self.doTransform([{u'type': u'row', 'children': [
                {u'type': u'group',
                 'data': {u'column-size': 20, u'layout-type': u'column'}},
            ]}]),
            [{u'type': u'row', 'class': 'row', 'children': [
                {u'type': u'group',
                 'data': {u'column-size': 20, u'layout-type': u'column'},
                 'class': 'cell width-20 position-0 overflowing'},
            ]}],
        )

    def doTransform(self, layout):
        dgrid = getUtility(IGridSystem, name='deco16_grid')
        newlayout = copy.deepcopy(layout)
        dgrid.transform(newlayout)
        return newlayout
