# -*- coding: utf-8 -*-

from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import MULTIPLE_GRIDS_INTEGRATION_TESTING
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import lxml
import unittest


def _has_classes(element, classes):
    element_classes = [c.strip() for c in element.attrib['class'].split(' ')]
    for expected in classes:
        if expected not in element_classes:
            raise Exception('expected (%s) in element classes (%s)' % (
                ' '.join(classes), ' '.join(element_classes)))
    return True


class GridTestCase(unittest.TestCase):

    layer = MULTIPLE_GRIDS_INTEGRATION_TESTING

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
        document = lxml.html.fromstring(self.view())

        rows = document.cssselect('#content div.row')
        cells0 = rows[0].cssselect('div.cell')
        cells1 = rows[1].cssselect('div.cell')
        cells2 = rows[2].cssselect('div.cell')

        self.assertTrue(_has_classes(cells0[0], ('width-16', 'position-0')))

        self.assertTrue(_has_classes(cells1[0], ('width-8', 'position-0')))
        self.assertTrue(_has_classes(cells1[1], ('width-8', 'position-8')))

        self.assertTrue(_has_classes(cells2[0], ('width-5', 'position-0')))
        self.assertTrue(_has_classes(cells2[1], ('width-5', 'position-5')))
        self.assertTrue(_has_classes(cells2[2], ('width-5', 'position-10')))

    def test_custom_grid(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        settings.grid_system = 'bootstrap3'

        document = lxml.html.fromstring(self.view())

        rows = document.cssselect('#content div.row')
        cells0 = rows[0].cssselect('div.cell')
        cells1 = rows[1].cssselect('div.cell')
        cells2 = rows[2].cssselect('div.cell')

        self.assertTrue(_has_classes(cells0[0], ('col-md-16',)))

        self.assertTrue(_has_classes(cells1[0], ('col-md-8',)))
        self.assertTrue(_has_classes(cells1[1], ('col-md-8',)))

        self.assertTrue(_has_classes(cells2[0], ('col-md-5',)))
        self.assertTrue(_has_classes(cells2[1], ('col-md-5',)))
        self.assertTrue(_has_classes(cells2[2], ('col-md-5',)))
