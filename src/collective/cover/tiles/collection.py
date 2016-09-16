# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
from plone.app.uuid.utils import uuidToObject
from plone.autoform import directives as form
from plone.memoize import view
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import queryUtility
from zope.deprecation.deprecation import deprecate
from zope.interface import implementer
from zope.schema import getFieldsInOrder

import random


class ICollectionTile(IPersistentCoverTile):

    """A tile that shows the result of a collection."""

    header = schema.TextLine(
        title=_(u'Header'),
        required=False,
    )

    form.omitted('title')
    form.no_omit(IDefaultConfigureForm, 'title')
    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    form.omitted('description')
    form.no_omit(IDefaultConfigureForm, 'description')
    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )

    form.omitted('date')
    form.no_omit(IDefaultConfigureForm, 'date')
    date = schema.Datetime(
        title=_(u'Date'),
        required=False,
    )

    form.omitted('image')
    form.no_omit(IDefaultConfigureForm, 'image')
    image = NamedImage(
        title=_(u'Image'),
        required=False,
    )

    # FIXME: this field should be named 'count'
    form.omitted('number_to_show')
    form.no_omit(IDefaultConfigureForm, 'number_to_show')
    number_to_show = schema.List(
        title=_(u'Number of items to display'),
        value_type=schema.TextLine(),
        required=False,
    )

    form.omitted('offset')
    form.no_omit(IDefaultConfigureForm, 'offset')
    offset = schema.Int(
        title=_(u'Start at item'),
        required=False,
        default=0,
    )

    form.omitted(IDefaultConfigureForm, 'random')
    random = schema.Bool(
        title=_(u'Select random items'),
        required=False,
        default=False
    )

    footer = schema.TextLine(
        title=_(u'Footer'),
        required=False,
        default=_(u'More…'),
    )

    uuid = schema.ASCIILine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


@implementer(ICollectionTile)
class CollectionTile(PersistentCoverTile):

    """A tile that shows the result of a collection."""

    index = ViewPageTemplateFile('templates/collection.pt')
    is_configurable = True
    is_editable = True
    short_name = _(u'msg_short_name_collection', default=u'Collection')

    def __call__(self):
        """Initialize configured_fields on each call."""
        self.configured_fields = self.get_configured_fields()
        return super(CollectionTile, self).__call__()

    def get_title(self):
        return self.data['title']

    def results(self):
        uuid = self.data.get('uuid', None)
        obj = uuidToObject(uuid)
        if obj is None:
            self.remove_relation()  # the referenced object was removed
            return []

        results = obj.results(batch=False)

        if self.data.get('random', False):
            # return a sample of the population
            size = min(self.count, len(results))
            return random.sample(results, size)

        # return a slice of the list
        start, end = self.offset, self.offset + self.count
        return results[start:end]

    @property
    def count(self):
        field = self.get_field_configuration('number_to_show')
        return int(field.get('size', 5))

    @property
    def offset(self):
        field = self.get_field_configuration('offset')
        return int(field.get('offset', 0))

    def is_empty(self):
        return (
            self.data.get('uuid', None) is None or
            uuidToObject(self.data.get('uuid')) is None
        )

    def populate_with_object(self, obj):
        super(CollectionTile, self).populate_with_object(obj)  # check permission
        if obj.portal_type in self.accepted_ct():
            data_mgr = ITileDataManager(self)
            data_mgr.set({
                'header': safe_unicode(obj.Title()),  # use collection's title
                'footer': _(u'More…'),  # XXX: field default's dont work, why?
                'uuid': IUUID(obj),
            })

    def accepted_ct(self):
        return ['Collection']

    def get_configured_fields(self):
        # Override this method, since we are not storing anything
        # in the fields, we just use them for configuration
        tileType = queryUtility(ITileType, name=self.__name__)
        conf = self.get_tile_configuration()

        fields = getFieldsInOrder(tileType.schema)

        results = []
        for name, obj in fields:
            field = {'id': name,
                     'title': obj.title}
            if name in conf:
                field_conf = conf[name]
                if ('visibility' in field_conf and field_conf['visibility'] == u'off'):
                    # If the field was configured to be invisible, then just
                    # ignore it
                    continue

                if 'htmltag' in field_conf:
                    # If this field has the capability to change its html tag
                    # render, save it here
                    field['htmltag'] = field_conf['htmltag']

                if 'imgsize' in field_conf:
                    field['scale'] = field_conf['imgsize']

                if 'format' in field_conf:
                    field['format'] = field_conf['format']

                if 'size' in field_conf:
                    field['size'] = field_conf['size']

                if 'offset' in field_conf:
                    field['offset'] = field_conf['offset']

            results.append(field)

        return results

    @view.memoize
    def thumbnail(self, item):
        """Return a thumbnail according to the tile configuration if
        the item has an image field and the field is configured as
        visible. Return the original image in case that's selected.

        :param item: [required]
        :type item: content object
        :returns: the scale object
        :rtype: ImageScale class
        """
        if self._has_image_field(item) and self._field_is_visible('image'):
            field = self.get_field_configuration('image')
            imgsize = field.get('imgsize', 'mini 200:200')

            # XXX: there's a bug here; same in list tile
            if imgsize == '_original':
                return None  # FIXME: should return original image

            # scale string is something like: 'mini 200:200'
            # we need the name only: 'mini'
            scale = imgsize.split(' ')[0]
            scales = item.restrictedTraverse('@@images')
            return scales.scale('image', scale)

    def get_alt(self, obj):
        """Return the alt attribute for the image in the obj."""
        return obj.Description() or obj.Title()

    @view.memoize
    def get_image_position(self):
        field = self.get_field_configuration('image')
        return field.get('position', 'left')

    def remove_relation(self):
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        if 'uuid' in old_data:
            old_data.pop('uuid')
        data_mgr.set(old_data)

    def show_header(self):
        return self._field_is_visible('header')

    @deprecate('Use url method instead')
    def collection_url(self):
        return self.url

    @property
    def url(self):
        """Return the URL of the referenced collection."""
        uuid = self.data.get('uuid', None)
        obj = uuidToObject(uuid)
        return obj.absolute_url() if obj else ''

    def show_footer(self):
        return self._field_is_visible('footer')
