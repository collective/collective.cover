# -*- coding: utf-8 -*-
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.calendar import CalendarTile
from collective.cover.tiles.calendar import ICalendarTile
from plone import api

import unittest


class CalendarTileTestCase(TestTileMixin, unittest.TestCase):
    def setUp(self):
        super(CalendarTileTestCase, self).setUp()
        self.tile = CalendarTile(self.cover, self.request)
        self.tile.__name__ = u"collective.cover.calendar"
        self.tile.id = u"test"

    @unittest.expectedFailure  # FIXME: raises BrokenImplementation
    def test_interface(self):
        self.interface = ICalendarTile
        self.klass = CalendarTile
        super(CalendarTileTestCase, self).test_interface()

    def test_default_configuration(self):
        self.assertFalse(self.tile.is_configurable)
        self.assertFalse(self.tile.is_editable)
        self.assertFalse(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(self.tile.accepted_ct(), [])

    def get_today_events(self, events):
        for week in events:
            for day in week:
                if "is_today" in day and day["is_today"]:
                    return day

    def test_getevents_for_calendar_first_weekday_6(self):
        api.portal.set_registry_record("plone.first_weekday", 6)
        with api.env.adopt_roles(["Manager"]):
            api.content.transition(self.portal["my-event"], "publish")
        events = self.tile.getEventsForCalendar()
        today_events = self.get_today_events(events)
        self.assertEqual(today_events["eventslist"][0]["title"], "My event")
