# -*- coding: utf-8 -*-

from zope import schema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover.tiles.list import ListTile, IListTile
from plone.uuid.interfaces import IUUID
from plone.tiles.interfaces import ITileDataManager

from collective.cover import _


class ICarouselTile(IListTile):
    """
    """

    uuids = schema.List(
        title=_(u'Elements'),
        value_type=schema.TextLine(),
        required=False,
        readonly=True,
    )

    autoplay = schema.Bool(
        title=_(u'Auto play'),
        required=False,
        default=True,
    )


class CarouselTile(ListTile):
    index = ViewPageTemplateFile("templates/carousel.pt")
    is_configurable = False
    is_editable = True

    def populate_with_object(self, obj):
        super(ListTile, self).populate_with_object(obj)  # check permission
        try:
            image_size = obj.restrictedTraverse('@@images').scale('image').size
            image_size = hasattr(image_size, '__call__') and image_size() or image_size
        except:
            image_size = None
        if not image_size:
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

    def get_uid(self, obj):
        return IUUID(obj)

    def init_js(self):
        return """
$(function() {
    Galleria.loadTheme("++resource++collective.cover/galleria-theme/galleria.cover_theme.js");
    Galleria.run('#galleria-%s .galleria-inner');

    if($('body').hasClass('template-view')) {
        Galleria.configure({ autoplay: %s });
    };
});
""" % (self.id, str(self.autoplay()).lower())
