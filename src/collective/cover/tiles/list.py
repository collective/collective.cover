# -*- coding: utf-8 -*-

from collective.cover import _
from collective.cover.interfaces import ICoverUIDsProvider
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
from plone.app.uuid.utils import uuidToObject
from plone.directives import form
from plone.memoize import view
from plone.namedfile.field import NamedBlobImage
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import queryUtility
from zope.interface import implements
from zope.schema import getFieldsInOrder


class IListTile(IPersistentCoverTile):

    uuids = schema.List(
        title=_(u'Elements'),
        value_type=schema.TextLine(),
        required=False,
    )

    # XXX: this field should be used to replace the 'limit' attribute
    form.omitted('count')
    form.no_omit(IDefaultConfigureForm, 'count')
    count = schema.Int(
        title=_(u'Number of items to display'),
        required=False,
        default=5,
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

    form.omitted('image')
    form.no_omit(IDefaultConfigureForm, 'image')
    image = NamedBlobImage(
        title=_(u'Image'),
        required=False,
    )

    form.omitted('date')
    form.no_omit(IDefaultConfigureForm, 'date')
    date = schema.Datetime(
        title=_(u'Date'),
        required=False,
    )


class ListTile(PersistentCoverTile):

    implements(IListTile)

    index = ViewPageTemplateFile('templates/list.pt')

    is_configurable = True
    is_droppable = True
    is_editable = False
    short_name = _(u'msg_short_name_list', default=u'List')
    limit = 5

    def results(self):
        """Return the list of objects stored in the tile as UUID. If an UUID
        has no object associated with it, removes the UUID from the list.

        :returns: a list of objects.
        """
        self.set_limit()
        uuids = self.data.get('uuids', None)
        result = []
        if uuids:
            uuids = [uuids] if type(uuids) == str else uuids
            for uid in uuids:
                obj = uuidToObject(uid)
                if obj:
                    result.append(obj)
                else:
                    self.remove_item(uid)
        return result[:self.limit]

    def is_empty(self):
        return self.results() == []

    # TODO: get rid of this by replacing it with the 'count' field
    def set_limit(self):
        for field in self.get_configured_fields():
            if field and field.get('id') == 'uuids':
                self.limit = int(field.get('size', self.limit))

    def populate_with_object(self, obj):
        super(ListTile, self).populate_with_object(obj)  # check permission
        uids = ICoverUIDsProvider(obj).getUIDs()
        if uids:
            self.populate_with_uids(uids)

    def populate_with_uids(self, uuids):
        self.set_limit()
        data_mgr = ITileDataManager(self)

        old_data = data_mgr.get()
        for uuid in uuids:
            if old_data['uuids']:
                if type(old_data['uuids']) != list:
                    old_data['uuids'] = [uuid]
                elif uuid not in old_data['uuids']:
                    old_data['uuids'].append(uuid)
            else:
                old_data['uuids'] = [uuid]
        data_mgr.set(old_data)

    def replace_with_objects(self, uids):
        super(ListTile, self).replace_with_objects(uids)  # check permission
        self.set_limit()
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        if type(uids) == list:
            old_data['uuids'] = [i for i in uids][:self.limit]
        else:
            old_data['uuids'] = [uids]

        data_mgr.set(old_data)

    def remove_item(self, uid):
        super(ListTile, self).remove_item(uid)
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        uids = data_mgr.get()['uuids']
        if uid in uids:
            del uids[uids.index(uid)]
        old_data['uuids'] = uids
        data_mgr.set(old_data)

    def get_uid(self, obj):
        """Return the UUID of the object.

        :param obj: [required]
        :type obj: content object
        :returns: the object's UUID
        """
        return IUUID(obj, None)

    # XXX: refactoring the tile's schema should be a way to avoid this
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

                if 'size' in field_conf:
                    field['size'] = field_conf['size']

            results.append(field)

        return results

    def thumbnail(self, item):
        """Return the thumbnail of an image if the item has an image field and
        the field is visible in the tile.

        :param item: [required]
        :type item: content object
        """
        if self._has_image_field(item) and self._field_is_visible('image'):
            tile_conf = self.get_tile_configuration()
            image_conf = tile_conf.get('image', None)
            if image_conf:
                scaleconf = image_conf['imgsize']
                # scale string is something like: 'mini 200:200' and
                # we need the name only: 'mini'
                scale = scaleconf.split(' ')[0]
                scales = item.restrictedTraverse('@@images')
                return scales.scale('image', scale)

    def _get_image_position(self):
        """Return the image position as configured on the tile.

        :returns: 'left' or 'right'
        """
        tile_conf = self.get_tile_configuration()
        image_conf = tile_conf.get('image', None)
        if image_conf:
            return image_conf.get('position', u'left')

    @view.memoize
    def get_image_position(self):
        return self._get_image_position()

    def _get_title_tag(self, item):
        """Return the HTML code used for the title as configured on the tile.

        :param item: [required]
        :type item: content object
        """
        tag = '<{heading}><a href="{href}">{title}</a></{heading}>'
        if self._field_is_visible('title'):
            tile_conf = self.get_tile_configuration()
            title_conf = tile_conf.get('title', None)
            if title_conf:
                heading = title_conf.get('htmltag', 'h2')
                href = item.absolute_url()
                title = item.Title()
                return tag.format(heading=heading, href=href, title=title)

    @view.memoize
    def get_title_tag(self, item):
        return self._get_title_tag(item)


class CollectionUIDsProvider(object):

    implements(ICoverUIDsProvider)

    def __init__(self, context):
        self.context = context

    def getUIDs(self):
        """ Return a list of UIDs of collection objects.
        """
        return [i.UID for i in self.context.queryCatalog()]


class FolderUIDsProvider(object):

    implements(ICoverUIDsProvider)

    def __init__(self, context):
        self.context = context

    def getUIDs(self):
        """ Return a list of UIDs of collection objects.
        """
        return [i.UID for i in self.context.getFolderContents()]


class GenericUIDsProvider(object):

    implements(ICoverUIDsProvider)

    def __init__(self, context):
        self.context = context

    def getUIDs(self):
        """ Return a list of UIDs of collection objects.
        """
        return [IUUID(self.context)]
