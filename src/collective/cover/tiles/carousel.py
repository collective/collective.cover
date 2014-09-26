# -*- coding: utf-8 -*-

from collective.cover import _
from collective.cover.interfaces import ITileEditForm
from collective.cover.tiles.list import IListTile
from collective.cover.tiles.list import ListTile
from collective.cover.widgets.interfaces import ITextLinesSortableWidget
from collective.cover.widgets.textlinessortable import TextLinesSortableFieldWidget
from plone.autoform import directives as form
from plone.tiles.interfaces import ITileDataManager
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.converter import BaseDataConverter
from zope import schema
from zope.component import adapts
from zope.interface import implements
from zope.schema.interfaces import IDict


# autoplay feature is enabled in view mode only
INIT_JS = """$(function() {{
    Galleria.loadTheme('++resource++collective.cover/galleria-theme/galleria.cover_theme.js');
    Galleria.run('#galleria-{0}');

    var options = {{ height: 1 }};
    if ($('body').hasClass('template-view')) {{
        options.autoplay = {1};
    }}
    Galleria.configure(options);
}});
"""


class ICarouselTile(IListTile):
    """A carousel based on the Galleria JavaScript image gallery framework.
    """

    autoplay = schema.Bool(
        title=_(u'Auto play'),
        required=False,
        default=True,
    )

    form.no_omit(ITileEditForm, 'uuids')
    form.widget(uuids=TextLinesSortableFieldWidget)


class CarouselTile(ListTile):

    implements(ICarouselTile)

    index = ViewPageTemplateFile('templates/carousel.pt')
    is_configurable = True
    is_editable = True
    short_name = _(u'msg_short_name_carousel', default=u'Carousel')

    def autoplay(self):
        if self.data['autoplay'] is None:
            return True  # default value

        return self.data['autoplay']

    def get_url(self, item):
        portal_properties = getToolByName(self.context, 'portal_properties')
        use_view_action = portal_properties.site_properties.getProperty(
            'typesUseViewActionInListings', ())
        url = item.absolute_url()
        if item.portal_type in use_view_action:
            url = url + '/view'
        uuid = self.get_uid(item)
        data_mgr = ITileDataManager(self)
        data = data_mgr.get()
        uuids = data['uuids']
        if uuid in uuids:
            if uuids[uuid].get('custom_url', u""):
                url = uuids[uuid].get('custom_url')
        return url

    def init_js(self):
        if self.is_empty():
            # Galleria will display scary error messages when it
            # cannot find its <div>.  So don't start galleria unless
            # the <div> is there and has some items in it.
            return ''

        return INIT_JS.format(self.id, str(self.autoplay()).lower())


class UUIDSFieldDataConverter(BaseDataConverter):
    """A data converter using the field's ``fromUnicode()`` method."""
    adapts(IDict, ITextLinesSortableWidget)

    def toWidgetValue(self, value):
        """Just dispatch it."""
        ordered_uuids = [(k, v) for k, v in value.items()]
        ordered_uuids.sort(key=lambda x: x[1]['order'])
        return '\r\n'.join([i[0] for i in ordered_uuids])

    def toFieldValue(self, value):
        """Just dispatch it."""
        if not len(value) or not isinstance(value, dict):
            return self.field.missing_value
        return value
