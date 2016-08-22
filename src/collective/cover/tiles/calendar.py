# -*- coding: utf-8 -*-
# Avoid to import wrong calendar module
# http://stackoverflow.com/a/8280677/2116850
from __future__ import absolute_import
from Acquisition import aq_inner
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from DateTime import DateTime
from plone import api
from plone.api.exc import InvalidParameterError
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from time import localtime
from urllib import quote_plus
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

import calendar


PLMF = MessageFactory('plonelocales')
EVENT_INTERFACES = [
    'plone.event.interfaces.IEvent', 'Products.ATContentTypes.interfaces.event.IATEvent']


def _catalog_counter_cachekey(method, self):
    """Return a cachekey based on catalog updates."""
    catalog = api.portal.get_tool('portal_catalog')
    return str(catalog.getCounter())


class ICalendarTile(IPersistentCoverTile):
    pass


@implementer(ICalendarTile)
class CalendarTile(PersistentCoverTile):
    """Calendar Tile code is coppied from plone.app.portlet Portlet Calendar
    """

    index = ViewPageTemplateFile('templates/calendar.pt')

    is_configurable = False
    is_editable = False
    is_droppable = False
    short_name = _(u'msg_short_name_calendar', default=u'Calendar')

    def __init__(self, context, request):
        super(CalendarTile, self).__init__(context, request)
        self._setup()

    def _setup(self):
        context = aq_inner(self.context)
        self._ts = getToolByName(context, 'translation_service')
        self.url_quote_plus = quote_plus

        self.now = localtime()
        self.yearmonth = yearmonth = self.getYearAndMonthToDisplay()
        self.year = year = yearmonth[0]
        self.month = month = yearmonth[1]

        self.showPrevMonth = yearmonth > (self.now[0] - 1, self.now[1])
        self.showNextMonth = yearmonth < (self.now[0] + 1, self.now[1])

        self.prevMonthYear, self.prevMonthMonth = self.getPreviousMonth(year, month)
        self.nextMonthYear, self.nextMonthMonth = self.getNextMonth(year, month)

        self.monthName = PLMF(self._ts.month_msgid(month),
                              default=self._ts.month_english(month))
        self._set_first_weekday()

    def _set_first_weekday(self):
        """Set calendar library first weekday for calendar."""
        try:  # Plone 5.x
            first_weekday = api.portal.get_registry_record('plone.first_weekday')
        except InvalidParameterError:
            try:  # plone.app.event
                first_weekday = api.portal.get_registry_record('plone.app.event.first_weekday')
            except InvalidParameterError:  # Plone 4.x
                portal_calendar = api.portal.get_tool('portal_calendar')
                first_weekday = getattr(portal_calendar, 'firstweekday', calendar.SUNDAY)
        calendar.setfirstweekday(first_weekday)

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []

    @ram.cache(_catalog_counter_cachekey)
    def getEvents(self):
        """Return all events in the selected month."""
        catalog = api.portal.get_tool('portal_catalog')
        _, last_day = calendar.monthrange(self.year, self.month)
        start = DateTime(self.year, self.month, 1)
        end = DateTime(self.year, self.month, last_day, 23, 59)
        query = dict(
            object_provides=EVENT_INTERFACES, review_state='published',
            start={'query': (start, end), 'range': 'min:max'}, sort_on='start')
        events = {}
        for brain in catalog(**query):
            day = brain.start.day()
            if day not in events:
                events[day] = []
            events[day].append(brain)
        return events

    def getEventsForCalendar(self):
        """Return the month data filled with events."""
        events = self.getEvents()
        monthcalendar = calendar.monthcalendar(self.year, self.month)
        weeks = []
        for w in monthcalendar:
            week = []
            for d in w:
                day = {'day': d, 'event': 0, 'eventslist': []}
                if d > 0:
                    day['is_today'] = self.isToday(d)
                day_events = []
                if d in events:
                    day_events = events[d]
                    day['date_string'] = '{0}-{1}-{2}'.format(self.year, self.month, d)
                    day['event'] += len(day_events)
                    day['eventslist'] = []
                    localized_date = self._ts.ulocalized_time(
                        day_events[0].start, context=self.context, request=self.request)
                    day['eventstring'] = localized_date
                for e in day_events:
                    event = dict(
                        start=e.start.Time(), end=e.end.Time(), title=e.Title or e.id)
                    day['eventslist'].append(event)
                    day['eventstring'] += '\n {0}'.format(self.getEventString(event))
                week.append(day)
            weeks.append(week)
        return weeks

    def getEventString(self, event):
        """Get event string to make event list hint on mouse over."""
        start = event['start'] and ':'.join(event['start'].split(':')[:2]) or ''
        end = event['end'] and ':'.join(event['end'].split(':')[:2]) or ''
        title = safe_unicode(event['title']) or u'event'

        if start and end:
            eventstring = '{0}-{1} {2}'.format(start, end, title)
        elif start:  # can assume not event['end']
            eventstring = '{0} - {1}'.format(start, title)
        elif event['end']:  # can assume not event['start']
            eventstring = '{0} - {1}'.format(title, end)
        else:  # can assume not event['start'] and not event['end']
            eventstring = title

        return eventstring

    def getYearAndMonthToDisplay(self):
        """Return calendar year and month."""
        request = self.request

        # First priority goes to the data in the REQUEST
        year = request.get('year', None)
        month = request.get('month', None)

        # Last resort to today
        if not year:
            year = self.now[0]
        if not month:
            month = self.now[1]

        # try to transform to number but fall back to current
        # date if this is ambiguous
        try:
            year, month = int(year), int(month)
        except (TypeError, ValueError):
            year, month = self.now[:2]

        # Finally return the results
        return year, month

    def getPreviousMonth(self, year, month):
        """Get previous month."""
        if month == 0 or month == 1:
            month, year = 12, year - 1
        else:
            month -= 1
        return (year, month)

    def getNextMonth(self, year, month):
        """Get next month."""
        if month == 12:
            month, year = 1, year + 1
        else:
            month += 1
        return (year, month)

    def getWeekdays(self):
        """Returns a list of Messages for the weekday names."""

        weekheaders = calendar.weekheader(3).split()
        weekdays = []
        for header in weekheaders:
            weekdays.append(PLMF('weekday_{0}_short'.format(header.lower()),
                                 default=header))
        return weekdays

    def isToday(self, day):
        """Returns True if the given day and the current month and year equals
           today, otherwise False.
        """
        return (
            self.now[2] == day and self.now[1] == self.month and self.now[0] == self.year)

    def getReviewStateString(self):
        """Get Review State String."""
        states = ['published']
        return ''.join(map(lambda x: 'review_state={0}&amp;'.format(self.url_quote_plus(x)), states))

    @ram.cache(_catalog_counter_cachekey)
    def getEventTypes(self):
        """Get a list of events portal types."""
        catalog = api.portal.get_tool('portal_catalog')
        query = dict(object_provides=EVENT_INTERFACES)
        types = set([b.portal_type for b in catalog(**query)])
        return ''.join(map(lambda x: 'Type={0}&amp;'.format(self.url_quote_plus(x)), types))

    def getQueryString(self):
        """Get current url get parameters."""
        request = self.request
        query_string = request.get('orig_query',
                                   request.get('QUERY_STRING', None))
        if len(query_string) == 0:
            query_string = ''
        else:
            query_string = '{0}&amp;'.format(query_string)
        return query_string
