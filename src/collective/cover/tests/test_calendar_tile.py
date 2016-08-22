# -*- coding: utf-8 -*-
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.calendar import CalendarTile
from collective.cover.tiles.calendar import ICalendarTile
from datetime import datetime
from plone import api
from tzlocal import get_localzone

import unittest


TZNAME = get_localzone().zone


class CalendarTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(CalendarTileTestCase, self).setUp()

        # Pin calendar to month 08/2016
        self.request['year'] = 2016
        self.request['month'] = 8

        # Create tile
        self.tile = CalendarTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.calendar'
        self.tile.id = u'test'

        # Pin today as day 18
        self.tile.isToday = lambda day: day == 18

        # create some events
        with api.env.adopt_roles(['Manager']):
            for i in [3, 12, 21, 30]:
                start = datetime(2016, 8, i, 10, 30)
                end = datetime(2016, 8, i, 11, 30)
                obj = api.content.create(
                    container=self.portal,
                    type='Event',
                    id='e{0}'.format(i),
                    startDate=start,  # Archetypes
                    endDate=end,
                    start=start,  # Dexterity
                    end=end,
                    timezone=TZNAME,
                )
                api.content.transition(obj, 'publish')

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

    def test_getEventsForCalendar(self):
        self.assertEqual(self.tile.getEventsForCalendar(), EXPECTED_CALENDAR)

    def test_getYearAndMonthToDisplay(self):
        self.assertEqual(self.tile.getYearAndMonthToDisplay(), (2016, 8))

    def test_getWeekdays(self):
        expected = [
            u'weekday_mon_short', u'weekday_tue_short', u'weekday_wed_short',
            u'weekday_thu_short', u'weekday_fri_short', u'weekday_sat_short',
            u'weekday_sun_short']
        self.assertEqual(self.tile.getWeekdays(), expected)

    def test_getReviewStateString(self):
        self.assertEqual(
            self.tile.getReviewStateString(), 'review_state=published&amp;')

    def test_getEventTypes(self):
        self.assertEqual(self.tile.getEventTypes(), 'Type=Event&amp;')


EXPECTED_CALENDAR = [
    [{'day': 1, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 2, 'event': 0, 'eventslist': [], 'is_today': False},
     {'date_string': '2016-8-3',
      'day': 3,
      'event': 1,
      'eventslist': [{'end': '11:30:00', 'start': '10:30:00', 'title': 'e3'}],
      'eventstring': u'Aug 03, 2016\n 10:30-11:30 e3',
      'is_today': False},
     {'day': 4, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 5, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 6, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 7, 'event': 0, 'eventslist': [], 'is_today': False}],
    [{'day': 8, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 9, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 10, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 11, 'event': 0, 'eventslist': [], 'is_today': False},
     {'date_string': '2016-8-12',
      'day': 12,
      'event': 1,
      'eventslist': [{'end': '11:30:00', 'start': '10:30:00', 'title': 'e12'}],
      'eventstring': u'Aug 12, 2016\n 10:30-11:30 e12',
      'is_today': False},
     {'day': 13, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 14, 'event': 0, 'eventslist': [], 'is_today': False}],
    [{'day': 15, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 16, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 17, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 18, 'event': 0, 'eventslist': [], 'is_today': True},
     {'day': 19, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 20, 'event': 0, 'eventslist': [], 'is_today': False},
     {'date_string': '2016-8-21',
      'day': 21,
      'event': 1,
      'eventslist': [{'end': '11:30:00', 'start': '10:30:00', 'title': 'e21'}],
      'eventstring': u'Aug 21, 2016\n 10:30-11:30 e21',
      'is_today': False}],
    [{'day': 22, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 23, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 24, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 25, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 26, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 27, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 28, 'event': 0, 'eventslist': [], 'is_today': False}],
    [{'day': 29, 'event': 0, 'eventslist': [], 'is_today': False},
     {'date_string': '2016-8-30',
      'day': 30,
      'event': 1,
      'eventslist': [{'end': '11:30:00', 'start': '10:30:00', 'title': 'e30'}],
      'eventstring': u'Aug 30, 2016\n 10:30-11:30 e30',
      'is_today': False},
     {'day': 31, 'event': 0, 'eventslist': [], 'is_today': False},
     {'day': 0, 'event': 0, 'eventslist': []},
     {'day': 0, 'event': 0, 'eventslist': []},
     {'day': 0, 'event': 0, 'eventslist': []},
     {'day': 0, 'event': 0, 'eventslist': []}]]
