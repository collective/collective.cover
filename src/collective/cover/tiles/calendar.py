# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer

try:  # plone.app.event
    from plone.app.event.portlets.portlet_calendar import Assignment
    from plone.app.event.portlets.portlet_calendar import Renderer
except ImportError:  # Plone 4.x
    from plone.app.portlets.portlets.calendar import Assignment
    from plone.app.portlets.portlets.calendar import Renderer


class ICalendarTile(IPersistentCoverTile):

    """A tile that shows a calendar of published events."""


@implementer(ICalendarTile)
class CalendarTile(PersistentCoverTile):

    """A tile that shows a calendar of published events.

    The implementation is a wraper of the calendar portlet.
    """

    index = ViewPageTemplateFile('templates/calendar.pt')
    is_configurable = False
    is_editable = False
    is_droppable = False
    short_name = _(u'msg_short_name_calendar', default=u'Calendar')

    def __call__(self, *args, **kwargs):
        self.setup()
        return super(CalendarTile, self).__call__(*args, **kwargs)

    def setup(self):
        helper = Renderer(self.context, self.request, None, None, Assignment())
        helper.update()

        self._ts = helper._ts
        self.url_quote_plus = helper.url_quote_plus

        self.now = helper.now
        self.year = year = helper.year
        self.month = month = helper.month

        self.showPrevMonth = helper.showPrevMonth
        self.showNextMonth = helper.showNextMonth

        self.prevMonthYear, self.prevMonthMonth = helper.getPreviousMonth(year, month)
        self.nextMonthYear, self.nextMonthMonth = helper.getNextMonth(year, month)

        self.monthName = helper.monthName

        self.getQueryString = helper.getQueryString
        self.getWeekdays = helper.getWeekdays
        self.getEventsForCalendar = helper.getEventsForCalendar
        self.getReviewStateString = helper.getReviewStateString
        self.getEventTypes = helper.getEventTypes

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []
