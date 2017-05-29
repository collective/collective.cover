# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.interfaces import ITileEditForm
from collective.cover.tiles.list import IListTile
from collective.cover.tiles.list import ListTile
from collective.cover.utils import get_types_use_view_action_in_listings
from collective.cover.widgets.interfaces import ITextLinesSortableWidget
from collective.cover.widgets.textlinessortable import TextLinesSortableFieldWidget
from plone.app.uuid.utils import uuidToObject
from plone.autoform import directives as form
from plone.tiles.interfaces import ITileDataManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.converter import BaseDataConverter
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.schema.interfaces import IDict


# autoplay feature is enabled in view mode only
INIT_JS = """$(function() {{
    Galleria.loadTheme('++resource++collective.cover/js/galleria.cover_theme.js');
    Galleria.run('#galleria-{0}');

    var options = {{ height: {1} }};
    if ($('body').hasClass('template-view')) {{
        options.autoplay = {2};
    }}
    Galleria.configure(options);
}});
"""


class ICarouselTile(IListTile):

    """A carousel based on the Galleria JS image gallery framework."""

    autoplay = schema.Bool(
        title=_(u'Auto play'),
        required=False,
        default=True,
    )

    form.no_omit(ITileEditForm, 'uuids')
    form.widget(uuids=TextLinesSortableFieldWidget)


@implementer(ICarouselTile)
class CarouselTile(ListTile):

    """A carousel based on the Galleria JS image gallery framework."""

    index = ViewPageTemplateFile('templates/carousel.pt')
    is_configurable = True
    is_editable = True
    short_name = _(u'msg_short_name_carousel', default=u'Carousel')

    def populate_with_object(self, obj):
        """Add an object to the carousel. This method will append new
        elements to the already existing list of items. If the object
        does not have an image associated, it will not be included and
        silently ignored.

        :param uuids: The list of objects' UUIDs to be used
        :type uuids: List of strings
        """
        super(ListTile, self).populate_with_object(obj)  # check permission
        if obj.portal_type == 'Collection':
            uuids = [i.UID for i in obj.queryCatalog()]
        else:
            uuids = [self.get_uuid(obj)]
        # accept just elements with a lead image
        uuids = [i for i in uuids if self._has_image_field(uuidToObject(i))]
        if uuids:
            self.populate_with_uuids(uuids)

    def autoplay(self):
        if self.data['autoplay'] is None:
            return True  # default value
        return self.data['autoplay']

    def get_title(self, item):
        """Get the title of the item, or the custom title if set.

        :param item: [required] The item for which we want the title
        :type item: Content object
        :returns: the item title
        :rtype: unicode
        """
        # First we get the title for the item itself
        title = item.Title()
        uuid = self.get_uuid(item)
        data_mgr = ITileDataManager(self)
        data = data_mgr.get()
        uuids = data['uuids']
        if uuid in uuids:
            if uuids[uuid].get('custom_title', u''):
                # If we had a custom title set, then get that
                title = uuids[uuid].get('custom_title')
        return title

    def get_description(self, item):
        """Get the description of the item, or the custom description
        if set.

        :param item: [required] The item for which we want the description
        :type item: Content object
        :returns: the item description
        :rtype: unicode
        """
        # First we get the url for the item itself
        description = item.Description()
        uuid = self.get_uuid(item)
        data_mgr = ITileDataManager(self)
        data = data_mgr.get()
        uuids = data['uuids']
        if uuid in uuids:
            if uuids[uuid].get('custom_description', u''):
                # If we had a custom description set, then get that
                description = uuids[uuid].get('custom_description')
        return description

    def get_url(self, item):
        """Get the URL of the item, or the custom URL if set.

        :param item: [required] The item for which we want the URL
        :type item: Content object
        :returns: the item URL
        :rtype: str
        """
        # First we get the url for the item itself
        url = item.absolute_url()
        if item.portal_type in get_types_use_view_action_in_listings():
            url += '/view'
        uuid = self.get_uuid(item)
        data_mgr = ITileDataManager(self)
        data = data_mgr.get()
        uuids = data['uuids']
        if uuid in uuids:
            if uuids[uuid].get('custom_url', u''):
                # If we had a custom url set, then get that
                url = uuids[uuid].get('custom_url')
        return url

    @property
    def get_image_ratio(self):
        """Return image ratio to be used in the carousel.
        See: http://galleria.io/docs/options/height/
        """
        thumbs = [self.thumbnail(i) for i in self.results()]
        # exclude from calculation any item with no image
        ratios = [
            float(t.height) / float(t.width) for t in thumbs if t is not None]
        if not ratios:
            return '1'
        return str(max(ratios))

    def init_js(self):
        if self.is_empty():
            # Galleria will display scary error messages when it
            # cannot find its <div>.  So don't start galleria unless
            # the <div> is there and has some items in it.
            return ''

        return INIT_JS.format(
            self.id, self.get_image_ratio, str(self.autoplay()).lower())


@adapter(IDict, ITextLinesSortableWidget)
class UUIDSFieldDataConverter(BaseDataConverter):

    """A data converter using the field's ``fromUnicode()`` method."""

    def toWidgetValue(self, value):
        """Convert the internal stored value into something that a
        z3c.form widget understands.

        :param value: [required] The internally stored value
        :type value: Dict
        :returns: A string with UUIDs separated by \r\n
        """

        # A new carousel tile has no items, populate_with_uuids has not been
        # called yet, so incoming uuids is not an empty dict() but None
        if value is None:
            return ''

        ordered_uuids = [(k, v) for k, v in value.items()]
        ordered_uuids.sort(key=lambda x: x[1]['order'])
        return '\r\n'.join([i[0] for i in ordered_uuids])

    def toFieldValue(self, value):
        """Pass the value extracted from the widget to the internal
        structure. In this case, the value expected is already formatted.

        :param value: [required] The data extracted from the widget
        :type value: Dict
        :returns: The value to be stored in the tile
        """
        if not len(value) or not isinstance(value, dict):
            return self.field.missing_value
        return value
