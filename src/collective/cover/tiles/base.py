# -*- coding: utf-8 -*-
# Basic implementation taken from
# http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.cover import _
from collective.cover.config import PROJECTNAME
from collective.cover.controlpanel import ICoverSettings
from collective.cover.tiles.configuration import ITilesConfigurationScreen
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
from collective.cover.tiles.permissions import ITilesPermissions
from plone import api
from plone.app.textfield.interfaces import ITransformer
from plone.app.textfield.value import RichTextValue
from plone.autoform import directives as form
from plone.memoize import view
from plone.namedfile import NamedBlobImage
from plone.namedfile.interfaces import INamedImage
from plone.namedfile.interfaces import INamedImageField
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from plone.tiles.esi import ESIPersistentTile
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from Products.CMFPlone.utils import safe_hasattr
from z3c.caching.interfaces import IPurgePaths
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import Choice
from zope.schema import getFieldNamesInOrder
from zope.schema import getFieldsInOrder

import logging
import Missing


logger = logging.getLogger(PROJECTNAME)


class IPersistentCoverTile(model.Schema):
    """
    Base interface for tiles that go into the cover object
    """

    css_class = Choice(
        title=_(u'CSS Class'),
        vocabulary='collective.cover.TileStyles',
        required=True,
        default=u'tile-default',
    )
    form.omitted('css_class')
    form.no_omit(IDefaultConfigureForm, 'css_class')
    form.widget(css_class='collective.cover.tiles.configuration_widgets.cssclasswidget.CSSClassFieldWidget')

    def populate_with_object(obj):
        """
        This method will take a CT object as parameter, and it will store the
        content into the tile. Each tile should implement its own method.
        """

    def delete():
        """ Remove the persistent data associated with the tile and notify the
        cover object was modified.
        """

    def accepted_ct():
        """Return a list of content types accepted by the tile. By default,
        all content types are acepted.
        """

    def get_tile_configuration():
        """
        A method that will return the configuration options for this tile
        """

    def set_tile_configuration(configuration):
        """
        A method that will set the configuration options for this tile
        """

    def get_configured_fields():
        """
        This method will return all fields that should be rendered and it will
        include specific configuration if any.
        Bear in mind, that in some specific cases, a visibility value can be
        off, and in that case, fields will not be included in the returned
        dictionary from this method
        """

    def setAllowedGroupsForEdit(groups):
        """
        This method assigns the groups that have edit permission to the tile
        """

    def getAllowedGroupsForEdit():
        """
        This method will return a list of groups that are allowed to edit the
        contents of this tile
        """

    def isAllowedToEdit(user):
        """
        This method returns true if the given user is allowed to edit the
        contents of the tile based on which group is he member of.
        If no user is provided, it will check on the authenticated member.
        """


@implementer(IPersistentCoverTile)
class PersistentCoverTile(ESIPersistentTile):

    is_configurable = False
    is_editable = True
    is_droppable = True
    css_class = None  # placeholder, we access it with tile's configuration
    # Short name for the tile.  Usually title minus 'Tile'.  Please
    # wrap this in _(...) so it can be translated.
    short_name = u''

    def populate_with_object(self, obj):
        if not self.isAllowedToEdit():
            raise Unauthorized(
                _('You are not allowed to add content to this tile'))

    def remove_item(self, uuid):
        if not self.isAllowedToEdit():
            raise Unauthorized(
                _('You are not allowed to remove content of this tile'))

    # XXX: the name of this method is really confusing as it does not deletes
    # the tile; rename it?
    def delete(self):
        """ Remove the persistent data associated with the tile and notify the
        cover object was modified.
        """
        logger.debug('Deleting tile {0}'.format(self.id))

        data_mgr = ITileDataManager(self)
        data_mgr.delete()

        # Remove permission data
        permissions = getMultiAdapter(
            (self.context, self.request, self), ITilesPermissions)
        permissions.delete()

        # Remove configuration data
        configuration = getMultiAdapter(
            (self.context, self.request, self), ITilesConfigurationScreen)
        configuration.delete()

        notify(ObjectModifiedEvent(self.context))

    @view.memoize
    def accepted_ct(self):
        """Return all content types available (default value)."""
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        return settings.searchable_content_types

    def is_compose_mode(self):
        """Return True if tile is being rendered in compose mode.
        """
        if 'PARENT_REQUEST' in self.context.REQUEST:
            # the name of the template is in the parent request
            url = self.context.REQUEST.PARENT_REQUEST.URL
            # compose mode is the last part of the URL
            return url.split('/')[-1] == 'compose'
        url = self.context.REQUEST.URL
        action = url.split('/')[-1]
        if action in ('@@updatelisttilecontent', '@@updatetilecontent',
                      '@@removeitemfromlisttile'):
            # update drag/drop, delete of list tile elements and dropping
            # content from the contentchooser on a tile. This is done with ajax
            # from the compose view where no PARENT_REQUEST is available
            return True
        return False

    def get_tile_configuration(self):
        tile_conf_adapter = getMultiAdapter(
            (self.context, self.request, self), ITilesConfigurationScreen)
        configuration = tile_conf_adapter.get_configuration()

        return configuration

    def set_tile_configuration(self, configuration):
        tile_conf_adapter = getMultiAdapter(
            (self.context, self.request, self), ITilesConfigurationScreen)
        tile_conf_adapter.set_configuration(configuration)

    def _get_tile_field_names(self):
        """Return a list of all the field names in the tile in schema order.
        """
        tile_type = getUtility(ITileType, name=self.__name__)

        return getFieldNamesInOrder(tile_type.schema)

    def _field_is_visible(self, field):
        """Return boolean according to the field visibility.
        """
        tile_conf = self.get_tile_configuration()
        field_conf = tile_conf.get(field, None)
        if field_conf:
            return field_conf.get('visibility', None) == u'on'
        else:
            return False

    def _has_image_field(self, obj):
        """Return True if the object has an image field.

        :param obj: [required]
        :type obj: content object
        """
        if safe_hasattr(obj, 'image'):  # Dexterity
            return True
        elif safe_hasattr(obj, 'Schema'):  # Archetypes
            return 'image' in obj.Schema().keys()
        else:
            return False

    def get_configured_fields(self):
        context = self.context
        tileType = queryUtility(ITileType, name=self.__name__)
        conf = self.get_tile_configuration()
        fields = getFieldsInOrder(tileType.schema)
        uuid = self.data.get('uuid', '')
        results = []
        for name, field in fields:
            image_field = INamedImageField.providedBy(field)
            data = self.data[name]
            if not ((image_field and (data or uuid)) or
                    (not image_field and data)):
                # If there's no data for this field, ignore it
                # special condition, if the field is an image field and
                # there is no uuid, then ignore it too
                continue

            if isinstance(data, RichTextValue):
                transformer = ITransformer(context, None)
                if transformer is not None:
                    content = transformer(data, 'text/x-html-safe')
            else:
                content = data

            field = {'id': name, 'content': content, 'title': field.title}

            if not self._include_updated_field(field, conf.get(name)):
                continue

            results.append(field)

        return results

    def _include_updated_field(self, field, field_conf):
        # Return True or False to say if the field should be included.
        # Possibly update the field argument that is passed in.

        if not field_conf:
            # By default all fields are included.
            return True

        if isinstance(field_conf, basestring):
            # css_class simply has a simple string, not a dictionary,
            # so there is nothing left to check.
            return True

        if (field_conf.get('visibility', '') == u'off'):
            # If the field was configured to be invisible, then just
            # ignore it
            return False

        if 'htmltag' in field_conf:
            # If this field has the capability to change its html tag
            # render, save it here
            field['htmltag'] = field_conf['htmltag']

        if 'format' in field_conf:
            field['format'] = field_conf['format']

        if 'imgsize' in field_conf:
            field['scale'] = field_conf['imgsize'].split()[0]

        if 'position' in field_conf:
            field['position'] = field_conf['position']

        return True

    def setAllowedGroupsForEdit(self, groups):
        permissions = getMultiAdapter(
            (self.context, self.request, self), ITilesPermissions)
        permissions.set_allowed_edit(groups)

    def getAllowedGroupsForEdit(self):
        permissions = getMultiAdapter(
            (self.context, self.request, self), ITilesPermissions)
        groups = permissions.get_allowed_edit()

        return groups

    def isAllowedToEdit(self, user=None):
        allowed = True

        pm = api.portal.get_tool('portal_membership')

        if user:
            if isinstance(user, basestring):
                user = pm.getMemberById(user)
        else:
            user = pm.getAuthenticatedMember()

        user_roles = user.getRoles()
        groups = self.getAllowedGroupsForEdit()

        if groups and 'Manager' not in user_roles:
            if not set(user.getGroups()).intersection(set(groups)):
                allowed = False

        return allowed

    def Date(self, brain):
        """Return the date of publication of the object referenced by
        brain. If the object has not been published yet, return its
        modification date. If the object is an Event, then return the
        start date.

        :param brain: [required] brain of the cataloged object
            referenced in the tile
        :type brain: AbstractCatalogBrain
        :returns: the object's publication/modification date or the
            event's start date in case of an Event-like object
        :rtype: str or DateTime
        """
        if brain.start == Missing.Value:
            return brain.Date() if callable(brain.Date) else brain.Date
        else:
            return brain.start

    def get_localized_time(self, datetime, format):
        """Return datetime localized as selected in layout configurations.

        :param datetime: [required] datetime to be formatted
        :type datetime: DateTime, datetime or date
        :param format: [required] format to be used
        :type format: string
        :returns: localized time
        :rtype: unicode
        """
        options = {
            'datetime': dict(  # u'Jul 15, 2015 01:23 PM'
                datetime=datetime, long_format=True, time_only=False),
            'dateonly': dict(  # u'Jul 15, 2015
                datetime=datetime, long_format=False, time_only=False),
            'timeonly': dict(  # u'01:23 PM'
                datetime=datetime, long_format=False, time_only=True),
        }
        return api.portal.get_localized_time(**options[format])

    @property
    def has_image(self):
        return self.data.get('image', None) is not None

    @property
    def scale(self):
        """Return the thumbnail scale to be used on the image field of the
        tile (if it has one).

        :returns: scale
        :rtype: string or None
        """
        tile_conf = self.get_tile_configuration()
        image_conf = tile_conf.get('image', None)
        if image_conf:
            scale = image_conf['imgsize']
            if scale == '_original':
                return None
            # scale string is something like: 'mini 200:200'
            return scale.split(' ')[0]  # we need the name only: 'mini'

    def get_image_data(self, obj):
        """Get image data from the object used to populate the tile.

        :param obj: object used to populate the tile
        :type obj: content type instance
        :returns: image
        :rtype: NamedBlobImage instance or None
        """
        image = None
        scale = self.scale
        # if has image, store a copy of its data
        if self._has_image_field(obj) and self._field_is_visible('image'):
            scales = obj.restrictedTraverse('@@images')
            image = scales.scale('image', scale)

        if image is not None and image != '':
            if isinstance(image.data, NamedBlobImage):
                # Dexterity
                image = image.data
            else:
                # Archetypes
                data = image.data
                if safe_hasattr(data, 'data'):  # image data weirdness...
                    data = data.data
                image = NamedBlobImage(data)
        return image

    def clear_scales(self):
        """Clear scales from storage."""
        from collective.cover.browser.scaling import AnnotationStorage
        storage = AnnotationStorage(self)
        for key in storage.keys():
            try:
                del storage[key]
            except KeyError:
                pass


@adapter(IPersistentCoverTile)
@implementer(IPurgePaths)
class PersistentCoverTilePurgePaths(object):
    """Paths to purge for cover tiles
    """

    def __init__(self, context):
        self.context = context

    def getRelativePaths(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        portal_url = api.portal.get().portal_url()
        prefix = context.url.replace(portal_url, '', 1)
        yield prefix
        for k, v in context.data.items():
            if INamedImage.providedBy(v):
                yield '{0}/@@images/image'.format(prefix)
                scales = parent.unrestrictedTraverse(
                    '{0}/{1}'.format(prefix.strip('/'), '@@images'))
                for size in scales.getAvailableSizes().keys():
                    yield '{0}/@@images/{1}'.format(prefix, size)

    def getAbsolutePaths(self):
        return []
