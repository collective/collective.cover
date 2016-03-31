# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.interfaces import ISearchableText
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.autoform.directives import write_permission
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implementer


class IEmbedTile(IPersistentCoverTile):

    write_permission(embed='collective.cover.EmbedCode')
    embed = schema.Text(
        title=_(u'Embedding code'),
        required=False,
    )

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )


@implementer(IEmbedTile)
class EmbedTile(PersistentCoverTile):

    index = ViewPageTemplateFile('templates/embed.pt')

    is_configurable = True
    is_editable = True
    is_droppable = False
    short_name = _(u'msg_short_name_embed', default=u'Embed')

    def is_empty(self):
        return not (self.data.get('embed', None) or
                    self.data.get('title', None) or
                    self.data.get('description', None))

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []


@implementer(ISearchableText)
class SearchableEmbedTile(object):

    def __init__(self, context):
        self.context = context

    def SearchableText(self):
        context = self.context
        return u'{0} {1}'.format(
            context.data['title'] or '', context.data['description'] or '')
