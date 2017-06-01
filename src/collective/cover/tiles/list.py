# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from collective.cover import _
from collective.cover.config import PROJECTNAME
from collective.cover.interfaces import ITileEditForm
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.autoform import directives as form
from plone.memoize import view
from plone.namedfile.field import NamedBlobImage
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import queryUtility
from zope.interface import implementer
from zope.schema import getFieldsInOrder

import logging
import warnings


logger = logging.getLogger(PROJECTNAME)


class IListTile(IPersistentCoverTile):

    uuids = schema.Dict(
        title=_(u'Elements'),
        key_type=schema.TextLine(),
        value_type=schema.Dict(
            key_type=schema.TextLine(),
            value_type=schema.TextLine(),
        ),
        required=False,
    )
    form.omitted('uuids')

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

    tile_title = schema.TextLine(title=_(u'Tile Title'), required=False)
    form.omitted('tile_title')
    form.no_omit(ITileEditForm, 'tile_title')

    more_link = schema.TextLine(title=_('Show more... link'), required=False)
    form.omitted('more_link')
    form.no_omit(ITileEditForm, 'more_link')
    form.widget(more_link='collective.cover.tiles.edit_widgets.more_link.MoreLinkFieldWidget')

    more_link_text = schema.TextLine(title=_('Show more... link text'), required=False)
    form.omitted('more_link_text')
    form.no_omit(ITileEditForm, 'more_link_text')


@implementer(IListTile)
class ListTile(PersistentCoverTile):

    index = ViewPageTemplateFile('templates/list.pt')

    is_configurable = True
    is_droppable = True
    is_editable = True
    short_name = _(u'msg_short_name_list', default=u'List')
    limit = 5

    def results(self):
        """Return the list of objects stored in the tile as UUID. If an UUID
        has no object associated with it, removes the UUID from the list.

        :returns: a list of objects.
        """
        self.set_limit()

        # always get the latest data
        uuids = ITileDataManager(self).get().get('uuids', None)

        results = list()
        if uuids:
            ordered_uuids = [(k, v) for k, v in uuids.items()]
            ordered_uuids.sort(key=lambda x: int(x[1]['order']))

            for uuid in [i[0] for i in ordered_uuids]:
                obj = uuidToObject(uuid)
                if obj:
                    results.append(obj)
                else:
                    # maybe the user has no permission to access the object
                    # so we try to get it bypassing the restrictions
                    catalog = api.portal.get_tool('portal_catalog')
                    brain = catalog.unrestrictedSearchResults(UID=uuid)
                    if not brain:
                        # the object was deleted; remove it from the tile
                        self.remove_item(uuid)
                        logger.debug(
                            'Nonexistent object {0} removed from '
                            'tile'.format(uuid)
                        )

        return results[:self.limit]

    def is_empty(self):
        return self.results() == []

    def Date(self, obj):
        # XXX: different from Collection tile, List tile returns objects
        #      instead of brains in its `results` function. I think we
        #      were looking for some performace gains there but in this
        #      case we need to go back to brains to avoid crazy stuff on
        #      trying to guess the name of the method returning the
        #      start date of an Event or an Event-like content type. We
        #      probably want to rewrite the `results` funtion but we have
        #      to be careful because there must be tiles derived from it,
        #      like the Carousel tile
        catalog = api.portal.get_tool('portal_catalog')
        brain = catalog(UID=self.get_uuid(obj))
        assert len(brain) == 1
        return super(ListTile, self).Date(brain[0])

    # TODO: get rid of this by replacing it with the 'count' field
    def set_limit(self):
        for field in self.get_configured_fields():
            if field and field.get('id') == 'uuids':
                self.limit = int(field.get('size', self.limit))

    def populate_with_object(self, obj):
        """ Add an object to the list of items

        :param obj: [required] The object to be added
        :type obj: Content object
        """
        super(ListTile, self).populate_with_object(obj)  # check permission
        self.populate_with_uuids([self.get_uuid(obj)])

    def populate_with_uuids(self, uuids):
        """ Add a list of elements to the list of items. This method will
        append new elements to the already existing list of items

        :param uuids: The list of objects' UUIDs to be used
        :type uuids: List of strings
        """
        if not self.isAllowedToEdit():
            raise Unauthorized(
                _('You are not allowed to add content to this tile'))
        self.set_limit()
        data_mgr = ITileDataManager(self)

        old_data = data_mgr.get()
        if old_data['uuids'] is None:
            # If there is no content yet, just assign an empty dict
            old_data['uuids'] = dict()

        uuids_dict = old_data.get('uuids')
        if not isinstance(uuids_dict, dict):
            # Make sure this is a dict
            uuids_dict = old_data['uuids'] = dict()

        if uuids_dict and len(uuids_dict) > self.limit:
            # Do not allow adding more objects than the defined limit
            return

        order_list = [int(val.get('order', 0))
                      for key, val in uuids_dict.items()]
        if len(order_list) == 0:
            # First entry
            order = 0
        else:
            # Get last order position and increment 1
            order_list.sort()
            order = order_list.pop() + 1

        for uuid in uuids:
            if uuid not in uuids_dict.keys():
                entry = dict()
                entry[u'order'] = unicode(order)
                uuids_dict[uuid] = entry
                order += 1

        old_data['uuids'] = uuids_dict
        data_mgr.set(old_data)

    def replace_with_uuids(self, uuids):
        """ Replaces the whole list of items with a new list of items

        :param uuids: The list of objects' UUIDs to be used
        :type uuids: List of strings
        """
        if not self.isAllowedToEdit():
            raise Unauthorized(
                _('You are not allowed to add content to this tile'))
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        # Clean old data
        old_data['uuids'] = dict()
        data_mgr.set(old_data)
        # Repopulate with clean list
        self.populate_with_uuids(uuids)

    def remove_item(self, uuid):
        """ Removes an item from the list

        :param uuid: [required] uuid for the object that wants to be removed
        :type uuid: string
        """
        super(ListTile, self).remove_item(uuid)  # check permission
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        uuids = data_mgr.get()['uuids']
        if uuid in uuids.keys():
            del uuids[uuid]
        old_data['uuids'] = uuids
        data_mgr.set(old_data)

    def get_uuid(self, obj):
        """Return the UUID of the object.

        :param obj: [required]
        :type obj: content object
        :returns: the object's UUID
        """
        return IUUID(obj, None)

    def get_alt(self, obj):
        """Return the alt attribute for the image in the obj."""
        return obj.Description() or obj.Title()

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

                if 'format' in field_conf:
                    field['format'] = field_conf['format']

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
                if scaleconf == '_original':
                    scale = None
                else:
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

    @property
    def tile_title(self):
        return self.data['tile_title']

    @property
    def more_link(self):
        if not (self.data['more_link'] and self.data['more_link_text']):
            return None

        pc = api.portal.get_tool('portal_catalog')
        brainz = pc(UID=self.data['more_link'])
        if not len(brainz):
            return None

        return {
            'href': brainz[0].getURL(),
            'text': self.data['more_link_text']
        }

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
    """CollectionUIDsProvider adapter will be removed in collective.cover v1.7."""
    warnings.warn(__doc__, DeprecationWarning)

    def __init__(self, context):
        pass

    def getUIDs(self):
        pass


class FolderUIDsProvider(object):
    """FolderUIDsProvider adapter will be removed in collective.cover v1.7."""
    warnings.warn(__doc__, DeprecationWarning)

    def __init__(self, context):
        pass

    def getUIDs(self):
        pass


class GenericUIDsProvider(object):
    """GenericUIDsProvider adapter will be removed in collective.cover v1.7."""
    warnings.warn(__doc__, DeprecationWarning)

    def __init__(self, context):
        pass

    def getUIDs(self):
        pass
