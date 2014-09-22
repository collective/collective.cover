# -*- coding: utf-8 -*-

from collective.cover import _
from collective.cover.interfaces import ITileEditForm
from collective.cover.tiles.list import IListTile
from collective.cover.tiles.list import ListTile
from collective.cover.widgets.textlinessortable import TextLinesSortableFieldWidget
from plone.memoize import view
from plone.autoform import directives as form
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements

# autoplay feature is enabled in view mode only
INIT_JS = """$(function() {{
    Galleria.loadTheme('++resource++collective.cover/galleria-theme/galleria.cover_theme.js');
    Galleria.run('#galleria-{0}');

    var options = {{ height: {1}, showInfo: {2} }};
    if ($('body').hasClass('template-view')) {{
        options.autoplay = {3};
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
    uuids = schema.List(
        title=_(u'Elements'),
        value_type=schema.TextLine(),
        required=False,
        readonly=False,
    )


class CarouselTile(ListTile):

    implements(ICarouselTile)

    index = ViewPageTemplateFile('templates/carousel.pt')
    is_configurable = True
    is_editable = True
    short_name = _(u'msg_short_name_carousel', default=u'Carousel')

    def populate_with_object(self, obj):
        super(CarouselTile, self).populate_with_object(obj)  # check permission
        try:
            scale = obj.restrictedTraverse('@@images').scale('image')
        except:
            scale = None
        if not scale:
            return
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

    def autoplay(self):
        if self.data['autoplay'] is None:
            return True  # default value

        return self.data['autoplay']

    def init_js(self):
        if self.is_empty():
            # Galleria will display scary error messages when it
            # cannot find its <div>.  So don't start galleria unless
            # the <div> is there and has some items in it.
            return ''

        return INIT_JS.format(self.id, str(self.get_image_ratio()),
                              self.show_info(), str(self.autoplay()).lower())

    def _get_description(self, item):
        """Return the HTML code used for the description as configured on the tile.

        :param item: [required]
        :type item: content object
        """
        if self._field_is_visible('description'):
            return item.Description()

    @view.memoize
    def get_description(self, item):
        return self._get_description(item)

    def get_image_ratio(self):
        ratio = 0.0
        items = self.results()
        for item in items:
            thumb = self.thumbnail(item)
            ratio = max(ratio, float(thumb.height)/float(thumb.width))
        if ratio:
            return ratio
        else:
            return 1

    def show_info(self):
        if not self._field_is_visible('title') and not self._field_is_visible('description'):
            return 'false'
        else:
            return 'true'

