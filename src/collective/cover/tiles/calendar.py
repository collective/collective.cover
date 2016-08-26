# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer

try:  # plone.app.event
    from plone.app.event.portlets.portlet_calendar import Assignment
    from plone.app.event.portlets.portlet_calendar import Renderer
    HAS_PLONE_APP_EVENT = True
except ImportError:  # Plone 4.x
    from plone.app.portlets.portlets.calendar import Assignment
    from plone.app.portlets.portlets.calendar import Renderer
    HAS_PLONE_APP_EVENT = False


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

        if HAS_PLONE_APP_EVENT:
            self.helper_template = helper.render
        else:
            self.helper_template = helper._template

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []
