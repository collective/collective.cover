# -*- coding: utf-8 -*-
from __future__ import absolute_import

from Acquisition import aq_inner
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from DateTime import DateTime
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_text
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from six.moves.urllib.parse import quote_plus
from time import localtime
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

import calendar


PLMF = MessageFactory("plonelocales")


class ICalendarTile(IPersistentCoverTile):
    pass


@implementer(ICalendarTile)
class CalendarTile(PersistentCoverTile):
    """Calendar Tile code is coppied from plone.app.portlet Portlet Calendar"""

    index = ViewPageTemplateFile("templates/calendar.pt")

    is_configurable = False
    is_editable = False
    is_droppable = False
    short_name = _(u"msg_short_name_calendar", default=u"Calendar")
    calendar_states = ("published",)
    calendar_types = ("Event",)

    def __init__(self, context, request):
        super(CalendarTile, self).__init__(context, request)
        self._setup()

    def _setup(self):
        context = aq_inner(self.context)
        self._ts = getToolByName(context, "translation_service")
        self.url_quote_plus = quote_plus

        self.first_weekday = api.portal.get_registry_record("plone.first_weekday")

        self.now = localtime()
        self.yearmonth = yearmonth = self.getYearAndMonthToDisplay()
        self.year = year = yearmonth[0]
        self.month = month = yearmonth[1]

        self.showPrevMonth = yearmonth > (self.now[0] - 1, self.now[1])
        self.showNextMonth = yearmonth < (self.now[0] + 1, self.now[1])

        self.prevMonthYear, self.prevMonthMonth = self.getPreviousMonth(year, month)
        self.nextMonthYear, self.nextMonthMonth = self.getNextMonth(year, month)

        self.monthName = PLMF(
            self._ts.month_msgid(month), default=self._ts.month_english(month)
        )

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []

    def getEventsForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        navigation_root_path = portal_state.navigation_root_path()
        weeks = self.old_getEventsForCalendar(month, year, path=navigation_root_path)

        for week in weeks:
            for day in week:
                daynumber = day["day"]
                if daynumber == 0:
                    continue
                day["is_today"] = self.isToday(daynumber)
                if day["event"]:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [
                        self._ts.ulocalized_time(
                            cur_date, context=context, request=self.request
                        )
                    ]
                    day["eventstring"] = "\n".join(
                        localized_date
                        + [
                            " {0}".format(self.getEventString(e))
                            for e in day["eventslist"]
                        ]
                    )
                    day["date_string"] = "{0}-{1}-{2}".format(year, month, daynumber)

        return weeks

    def old_getEventsForCalendar(self, month="1", year="2002", **kw):
        """recreates a sequence of weeks, by days each day is a mapping.
        {'day': #, 'url': None}
        """
        year = int(year)
        month = int(month)
        # daysByWeek is a list of days inside a list of weeks, like so:
        # [[0, 1, 2, 3, 4, 5, 6],
        #  [7, 8, 9, 10, 11, 12, 13],
        #  [14, 15, 16, 17, 18, 19, 20],
        #  [21, 22, 23, 24, 25, 26, 27],
        #  [28, 29, 30, 31, 0, 0, 0]]

        calendar.setfirstweekday(self.first_weekday)
        daysByWeek = calendar.monthcalendar(year, month)
        weeks = []

        events = self.old_catalog_getevents(year, month, **kw)

        for week in daysByWeek:
            days = []
            for day in week:
                if day in events:
                    days.append(events[day])
                else:
                    days.append({"day": day, "event": 0, "eventslist": []})

            weeks.append(days)

        return weeks

    def old_catalog_getevents(self, year, month, **kw):
        """given a year and month return a list of days that have events"""
        # XXX: this method violates the rules for tools/utilities:
        # it depends on a non-utility tool
        year = int(year)
        month = int(month)
        last_day = calendar.monthrange(year, month)[1]
        first_date = self.old_getBeginAndEndTimes(1, month, year)[0]
        last_date = self.old_getBeginAndEndTimes(last_day, month, year)[1]

        query_args = {
            "portal_type": self.calendar_types,
            "review_state": self.calendar_states,
            "start": {"query": last_date, "range": "max"},
            "end": {"query": first_date, "range": "min"},
            "sort_on": "start",
        }
        query_args.update(kw)

        ctool = getToolByName(self, "portal_catalog")
        query = ctool(**query_args)

        # compile a list of the days that have events
        eventDays = {}
        for daynumber in range(1, 32):  # 1 to 31
            eventDays[daynumber] = {"eventslist": [], "event": 0, "day": daynumber}
        includedevents = []
        for result in query:
            if result.getRID() in includedevents:
                break
            else:
                includedevents.append(result.getRID())
            event = {}
            # we need to deal with events that end next month
            if result.end.month != month:
                # doesn't work for events that last ~12 months
                # fix it if it's a problem, otherwise ignore
                eventEndDay = last_day
                event["end"] = None
            else:
                eventEndDay = result.end.day
                event["end"] = result.end.time()
            # and events that started last month
            if result.start.month != month:  # same as above (12 month thing)
                eventStartDay = 1
                event["start"] = None
            else:
                eventStartDay = result.start.day
                event["start"] = result.start.time()

            event["title"] = result.Title or result.getId

            if eventStartDay != eventEndDay:
                allEventDays = range(eventStartDay, eventEndDay + 1)
                eventDays[eventStartDay]["eventslist"].append(
                    {"end": None, "start": result.start.time(), "title": event["title"]}
                )
                eventDays[eventStartDay]["event"] = 1

                for eventday in allEventDays[1:-1]:
                    eventDays[eventday]["eventslist"].append(
                        {"end": None, "start": None, "title": event["title"]}
                    )
                    eventDays[eventday]["event"] = 1

                if result.end == result.end.replace(hour=0, minute=0, second=0):
                    last_day_data = eventDays[allEventDays[-2]]
                    last_days_event = last_day_data["eventslist"][-1]
                    last_days_event["end"] = (
                        (result.end - 1).replace(hour=23, minute=59, second=59).time()
                    )
                else:
                    eventDays[eventEndDay]["eventslist"].append(
                        {
                            "end": result.end.time(),
                            "start": None,
                            "title": event["title"],
                        }
                    )
                    eventDays[eventEndDay]["event"] = 1
            else:
                eventDays[eventStartDay]["eventslist"].append(event)
                eventDays[eventStartDay]["event"] = 1
            # This list is not uniqued and isn't sorted
            # uniquing and sorting only wastes time
            # and in this example we don't need to because
            # later we are going to do an 'if 2 in eventDays'
            # so the order is not important.
            # example:  [23, 28, 29, 30, 31, 23]
        return eventDays

    def old_getBeginAndEndTimes(self, day, month, year):
        """Get two DateTime objects representing the beginning and end
        of the given day
        """
        day = int(day)
        month = int(month)
        year = int(year)

        begin = DateTime("{0}/{1:02d}/{2:02d} 00:00:00".format(year, month, day))
        end = DateTime("{0}/{1:02d}/{2:02d} 23:59:59".format(year, month, day))

        return (begin, end)

    def getEventString(self, event):
        start = event["start"] and ":".join(str(event["start"]).split(":")[:2]) or ""
        end = event["end"] and ":".join(str(event["end"]).split(":")[:2]) or ""
        title = safe_text(event["title"]) or u"event"

        if start and end:
            eventstring = "{0}-{1} {2}".format(start, end, title)
        elif start:  # can assume not event['end']
            eventstring = "{0} - {1}".format(start, title)
        elif event["end"]:  # can assume not event['start']
            eventstring = "{0} - {1}".format(title, end)
        else:  # can assume not event['start'] and not event['end']
            eventstring = title

        return eventstring

    def getYearAndMonthToDisplay(self):
        session = None
        request = self.request

        # First priority goes to the data in the REQUEST
        year = request.get("year", None)
        month = request.get("month", None)
        use_session = False

        # Next get the data from the SESSION
        if use_session:
            session = request.get("SESSION", None)
            if session:
                if not year:
                    year = session.get("calendar_year", None)
                if not month:
                    month = session.get("calendar_month", None)

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

        # Store the results in the session for next time
        if session:
            session.set("calendar_year", year)
            session.set("calendar_month", month)

        # Finally return the results
        return year, month

    def getPreviousMonth(self, year, month):
        if month == 0 or month == 1:
            month, year = 12, year - 1
        else:
            month -= 1
        return (year, month)

    def getNextMonth(self, year, month):
        if month == 12:
            month, year = 1, year + 1
        else:
            month += 1
        return (year, month)

    def getWeekdays(self):
        """Returns a list of Messages for the weekday names."""
        weekdays = []
        # In TranslationServiceTool, Sunday is 0. So we need to add +1 to first_weekday.
        first_weekday_ts = self.first_weekday + 1
        day_numbers = [i % 7 for i in range(first_weekday_ts, first_weekday_ts + 7)]

        # list of ordered weekdays as numbers
        for day in day_numbers:
            weekdays.append(
                PLMF(
                    self._ts.day_msgid(day, format="s"),
                    default=self._ts.weekday_english(day, format="a"),
                )
            )
        return weekdays

    def isToday(self, day):
        """Returns True if the given day and the current month and year equals
        today, otherwise False.
        """
        return (
            self.now[2] == day
            and self.now[1] == self.month
            and self.now[0] == self.year
        )

    def getReviewStateString(self):
        states = self.calendar_states
        return "".join(
            map(lambda x: "review_state={0}".format(self.url_quote_plus(x)), states)
        )

    def getEventTypes(self):
        types = self.calendar_types
        return "".join(
            map(lambda x: "Type={0}&amp;".format(self.url_quote_plus(x)), types)
        )

    def getQueryString(self):
        request = self.request
        query_string = request.get("orig_query", request.get("QUERY_STRING", None))
        if len(query_string) == 0:
            query_string = ""
        else:
            query_string = "{0}&amp;".format(query_string)
        return query_string
