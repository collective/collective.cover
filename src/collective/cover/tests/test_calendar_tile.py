# -*- coding: utf-8 -*-
from collective.cover.tests.base import TestTileMixin
from collective.cover.tiles.calendar import CalendarTile
from collective.cover.tiles.calendar import ICalendarTile

import unittest


class CalendarTileTestCase(TestTileMixin, unittest.TestCase):

    def setUp(self):
        super(CalendarTileTestCase, self).setUp()
        self.tile = CalendarTile(self.cover, self.request)
        self.tile.__name__ = u'collective.cover.calendar'
        self.tile.id = u'test'

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


# load tests only in Plone < 5
def test_suite():
    # FIXME: https://github.com/collective/collective.cover/issues/633
    from collective.cover.config import IS_PLONE_5
    if IS_PLONE_5:
        return unittest.TestSuite()

    return unittest.defaultTestLoader.loadTestsFromName(__name__)
