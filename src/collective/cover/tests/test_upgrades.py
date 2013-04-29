# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.upgrades import register_available_tiles_record
from plone.registry.interfaces import IRecordAddedEvent
from plone.registry.interfaces import IRegistry
from zope.component import eventtesting
from zope.component import getUtility

import unittest


class Upgrade2to3TestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_register_available_tiles_record(self):
        registry = getUtility(IRegistry)
        record = 'collective.cover.controlpanel.ICoverSettings.available_tiles'

        eventtesting.setUp()
        # calling the handler here should have no effect as we are running the
        # latest profile version
        register_available_tiles_record(self.portal)
        events = eventtesting.getEvents(IRecordAddedEvent)
        self.assertEqual(len(events), 0)
        eventtesting.clearEvents()

        # now we delete the record and rerun the handler to verify the record
        # was added
        del registry.records[record]
        register_available_tiles_record(self.portal)
        events = eventtesting.getEvents(IRecordAddedEvent)
        self.assertEqual(len(events), 1)
        self.assertIn(record, registry.records)
        eventtesting.clearEvents()
