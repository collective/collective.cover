# -*- coding: UTF-8 -*-
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from plone.tiles.interfaces import ITile


@adapter(ITile, IObjectModifiedEvent)
def notifyModified(tile, event):
    # Make sure the page's modified date gets updated, necessary in cache purge
    # cases by eg
    tile.__parent__.notifyModified()
