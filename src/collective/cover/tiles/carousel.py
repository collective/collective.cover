# -*- coding: utf-8 -*-

from collective.cover import _
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
    """
    """

    autoplay = schema.Bool(
        title=_(u'Auto play'),
        required=False,
        default=True,
    )

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
        return """
$(function() {{
    Galleria.loadTheme("++resource++collective.cover/galleria-theme/galleria.cover_theme.js");
    Galleria.run('#galleria-{0} .galleria-inner');

    if($('body').hasClass('template-view')) {{
        Galleria.configure({{ autoplay: {1} }});
    }};
}});
""".format(self.id, str(self.autoplay()).lower())
