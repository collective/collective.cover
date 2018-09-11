# -*- coding: utf-8 -*-
from collective.cover.config import DEFAULT_GRID_SYSTEM
from collective.cover.config import IS_PLONE_5
from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import lxml  # nosec
import unittest


def _has_classes(element, classes):
    element_classes = [c.strip() for c in element.attrib['class'].split(' ')]
    for expected in classes:
        if expected not in element_classes:
            raise Exception('expected ({0}) in element classes ({1})'.format(
                ' '.join(classes), ' '.join(element_classes)))
    return True


class GridTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']

        with api.env.adopt_roles(['Manager']):
            folder = api.content.create(portal, 'Folder', 'folder')

        api.content.create(
            folder,
            'collective.cover.content',
            'cover',
            template_layout='Layout A',
        )

        self.view = folder.cover.restrictedTraverse('view')

    def test_default_grid(self):
        if IS_PLONE_5:
            self.assertEqual(DEFAULT_GRID_SYSTEM, 'bootstrap3')
        else:
            self.assertEqual(DEFAULT_GRID_SYSTEM, 'deco16_grid')

    def _switch_grid_system(self, grid):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        settings.grid_system = grid

    def test_deco16_grid(self):
        self._switch_grid_system('deco16_grid')

        document = lxml.html.fromstring(self.view())
        rows = document.cssselect('#content div.row')
        cells0 = rows[0].cssselect('div.cell')
        cells1 = rows[1].cssselect('div.cell')
        cells2 = rows[2].cssselect('div.cell')

        self.assertTrue(_has_classes(cells0[0], ('width-12', 'position-0')))
        self.assertTrue(_has_classes(cells1[0], ('width-6', 'position-0')))
        self.assertTrue(_has_classes(cells1[1], ('width-6', 'position-6')))
        self.assertTrue(_has_classes(cells2[0], ('width-4', 'position-0')))
        self.assertTrue(_has_classes(cells2[1], ('width-4', 'position-4')))
        self.assertTrue(_has_classes(cells2[2], ('width-4', 'position-8')))

    def test_bootstrap3_grid(self):
        self._switch_grid_system('bootstrap3')

        document = lxml.html.fromstring(self.view())
        rows = document.cssselect('#content div.row')
        cells0 = rows[0].cssselect('div.column')
        cells1 = rows[1].cssselect('div.column')
        cells2 = rows[2].cssselect('div.column')

        self.assertTrue(_has_classes(cells0[0], ('col-md-12',)))
        self.assertTrue(_has_classes(cells1[0], ('col-md-6',)))
        self.assertTrue(_has_classes(cells1[1], ('col-md-6',)))
        self.assertTrue(_has_classes(cells2[0], ('col-md-4',)))
        self.assertTrue(_has_classes(cells2[1], ('col-md-4',)))
        self.assertTrue(_has_classes(cells2[2], ('col-md-4',)))

    def test_bootstrap2_grid(self):
        self._switch_grid_system('bootstrap2')

        document = lxml.html.fromstring(self.view())
        rows = document.cssselect('#content div.row')
        cells0 = rows[0].cssselect('div.column')
        cells1 = rows[1].cssselect('div.column')
        cells2 = rows[2].cssselect('div.column')

        self.assertTrue(_has_classes(cells0[0], ('span12',)))
        self.assertTrue(_has_classes(cells1[0], ('span6',)))
        self.assertTrue(_has_classes(cells1[1], ('span6',)))
        self.assertTrue(_has_classes(cells2[0], ('span4',)))
        self.assertTrue(_has_classes(cells2[1], ('span4',)))
        self.assertTrue(_has_classes(cells2[2], ('span4',)))
