# -*- coding: utf-8 -*-

from collective.cover.tiles.base import IPersistentCoverTile
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


@adapter(IPersistentCoverTile, IObjectModifiedEvent)
def notifyModified(tile, event):
    # Make sure the page's modified date gets updated, necessary in cache purge
    # cases by eg
    tile.__parent__.notifyModified()
