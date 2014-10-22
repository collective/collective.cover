# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.interfaces import ITileEditForm
from collective.cover.tiles.list import IListTile
from collective.cover.tiles.list import ListTile
from collective.cover.widgets.textlinessortable import TextLinesSortableFieldWidget
from plone.autoform import directives as form
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements


class ICarouselTile(IListTile):

    """A carousel based on the Cycle2 slideshow plugin for jQuery."""

    form.omitted('autoplay')
    form.no_omit(ITileEditForm, 'autoplay')
    autoplay = schema.Bool(
        title=_(u'Auto play'),
        default=False,
        required=False,
    )

    form.no_omit(ITileEditForm, 'uuids')
    form.widget(uuids=TextLinesSortableFieldWidget)
    uuids = schema.List(
        title=_(u'Elements'),
        value_type=schema.TextLine(),
        required=False,
        readonly=False,
    )


class CarouselTile(ListTile):

    """A carousel based on the Cycle2 slideshow plugin for jQuery."""

    implements(ICarouselTile)
    index = ViewPageTemplateFile('templates/carousel.pt')
    is_configurable = True
    is_editable = True
    short_name = _(u'msg_short_name_carousel', default=u'Carousel')

    def populate_with_object(self, obj):
        super(CarouselTile, self).populate_with_object(obj)  # check permission

        self.set_limit()
        uuid = IUUID(obj, None)
        data_mgr = ITileDataManager(self)

        old_data = data_mgr.get()
        if data_mgr.get()['uuids']:
            uuids = data_mgr.get()['uuids']
            if type(uuids) != list:
                uuids = [uuid]
            elif uuid not in uuids:
                uuids.append(uuid)

            old_data['uuids'] = uuids[:self.limit]
        else:
            old_data['uuids'] = [uuid]
        data_mgr.set(old_data)

    @property
    def paused(self):
        """Return True if the carousel will begin in a paused state."""
        paused = not self.data.get('autoplay', False)
        return str(paused).lower()
