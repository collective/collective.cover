# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
from plone.app.standardtiles.rss import IRSSTile as IRSSTileBase
from plone.app.standardtiles.rss import RSSTile as RSSTileBase
from plone.directives import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class IRSSTile(IRSSTileBase, IPersistentCoverTile):

    form.omitted(IDefaultConfigureForm, 'portlet_title')
    form.omitted(IDefaultConfigureForm, 'count')
    form.omitted(IDefaultConfigureForm, 'url')
    form.omitted(IDefaultConfigureForm, 'timeout')


class RSSTile(RSSTileBase, PersistentCoverTile):

    implements(IRSSTile)

    index = ViewPageTemplateFile('templates/rss.pt')

    is_configurable = True
    short_name = _(u'msg_short_name_basic', default=u'RSS')

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []
