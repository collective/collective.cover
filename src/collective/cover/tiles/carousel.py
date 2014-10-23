# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.interfaces import ITileEditForm
from collective.cover.tiles.list import IListTile
from collective.cover.tiles.list import ListTile
from collective.cover.widgets.textlinessortable import TextLinesSortableFieldWidget
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
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

    pager_style = schema.Choice(
        title=_(u'Pager'),
        vocabulary='collective.cover.PagerStyles',
        required=True,
        default=u'Thumbnails',
    )
    form.omitted('pager_style')
    form.no_omit(IDefaultConfigureForm, 'pager_style')
    form.widget(pager_style='collective.cover.tiles.configuration_widgets.cssclasswidget.CSSClassFieldWidget')

    overlay = schema.SourceText(
        title=_(u'Overlay Template'),
        required=False,
        default=u'<div>{{title}}</div><div>{{desc}}</div>',
    )
    form.omitted('overlay')
    form.no_omit(IDefaultConfigureForm, 'overlay')


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

    def pagerclass(self):
        #pager_style = self.data.get('pager_style', None)
        #if pager_style is None:
            #return 'dots'  # default value

        #return pager_style.lower()
        return "thumbnails"
    
    def pagerthumbnail(self, item):
        """Return the thumbnail of an image if the item has an image field, the
        pager_style is 'Thumbnails' and the pager is visible. 

        :param item: [required]
        :type item: content object
        """
        #pager_style = self.data.get('pager_style', None)
        #if pager_style is None or pager_style != 'Thumbnails':
            
            #return None  # skip expensive image processing

        #if not (self._has_image_field(item) and
                #self._field_is_visible('pager_style')):
            #return None
            
        scales = item.restrictedTraverse('@@images')
        return scales.scale('image', width=49, height=49, direction='down')
    
    def pagertemplate(self):
        #pager_style = self.data.get('pager_style', None)
        #if pager_style is None or pager_style == 'Dots':
            #return "<span>&bull;</span>"
        #elif pager_style == 'Numbers':
            #return "<strong><a href=#> {{slideNum}} </a></strong>"
        #elif pager_style == 'Thumbnails':
            #return "<a href='#'><img src='{{thumbnail}}' width=49 height=49></a>"
        return "<a href='#'><img src='{{thumbnail}}' width=49 height=49></a>"
