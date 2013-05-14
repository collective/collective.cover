# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.upgrades import register_available_tiles_record
from collective.cover.upgrades import register_styles_record
from collective.cover.upgrades import rename_content_chooser_resources
from plone.registry.interfaces import IRecordAddedEvent
from plone.registry.interfaces import IRegistry
from zope.component import eventtesting
from zope.component import getUtility

import unittest


class Upgrade2to3TestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_rename_content_chooser_resources(self):
        # writing a real test for this will need a mock tool for
        # ResourceRegistries and I don't think it worths the time, so just
        # call the function and check it runs with no errors
        css_tool = self.portal['portal_css']
        js_tool = self.portal['portal_javascripts']
        rename_content_chooser_resources(self.portal)
        self.assertNotIn(
            '++resource++collective.cover/screenlets.css',
            css_tool.getResourceIds()
        )
        self.assertNotIn(
            '++resource++collective.cover/screenlets.js',
            js_tool.getResourceIds()
        )
        self.assertIn(
            '++resource++collective.cover/contentchooser.css',
            css_tool.getResourceIds()
        )
        self.assertIn(
            '++resource++collective.cover/contentchooser.js',
            js_tool.getResourceIds()
        )

    def test_register_available_tiles_record(self):
        registry = getUtility(IRegistry)
        record = 'collective.cover.controlpanel.ICoverSettings.available_tiles'

        eventtesting.setUp()

        # calling the handler here should have no effect as we are running the
        # latest profile version
        eventtesting.clearEvents()
        register_available_tiles_record(self.portal)
        events = eventtesting.getEvents(IRecordAddedEvent)
        self.assertEqual(len(events), 0)

        # now we delete the record and rerun the handler to verify the record
        # was added
        del registry.records[record]
        eventtesting.clearEvents()
        register_available_tiles_record(self.portal)
        events = eventtesting.getEvents(IRecordAddedEvent)
        self.assertNotEqual(len(events), 0)
        self.assertIn(record, registry.records)
        eventtesting.clearEvents()

    def test_register_styles_record(self):
        registry = getUtility(IRegistry)
        record = 'collective.cover.controlpanel.ICoverSettings.styles'

        eventtesting.setUp()

        # calling the handler here should have no effect as we are running the
        # latest profile version
        eventtesting.clearEvents()
        register_styles_record(self.portal)
        events = eventtesting.getEvents(IRecordAddedEvent)
        self.assertEqual(len(events), 0)

        # now we delete the record and rerun the handler to verify the record
        # was added
        del registry.records[record]
        eventtesting.clearEvents()
        register_styles_record(self.portal)
        events = eventtesting.getEvents(IRecordAddedEvent)
        self.assertNotEqual(len(events), 0)
        self.assertIn(record, registry.records)
        eventtesting.clearEvents()
