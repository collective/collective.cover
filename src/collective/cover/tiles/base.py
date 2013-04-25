# -*- coding: utf-8 -*-

# Basic implementation taken from
# http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts

import logging

from logging import exception
from AccessControl import Unauthorized
from Acquisition import aq_base, aq_parent
from ZODB.POSException import ConflictError

from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component import getUtility

from zope.event import notify

from zope.interface import implements
from zope.interface import Interface

from zope.lifecycleevent import ObjectModifiedEvent

from zope.schema import getFieldsInOrder

from zope.annotation import IAnnotations
from persistent.dict import PersistentDict
from zope.publisher.interfaces import NotFound

from plone import tiles
from plone.tiles.esi import ESITile

from plone.app.textfield.interfaces import ITransformer
from plone.app.textfield.value import RichTextValue

from plone.tiles.interfaces import ITileType

from plone.tiles.interfaces import ITileDataManager

from plone.scale.scale import scaleImage
from plone.scale.storage import AnnotationStorage as BaseAnnotationStorage
from plone.namedfile.scaling import ImageScale as BaseImageScale
from plone.namedfile.scaling import ImageScaling as BaseImageScaling
from plone.namedfile.utils import set_headers, stream_data
from plone.namedfile.interfaces import INamedImage
from plone.rfc822.interfaces import IPrimaryFieldInfo

from Products.CMFCore.utils import getToolByName

from collective.cover.config import PROJECTNAME
from collective.cover.tiles.configuration import ITilesConfigurationScreen
from collective.cover.tiles.permissions import ITilesPermissions

from collective.cover import _
from z3c.caching.interfaces import IPurgePaths
from zope.component import adapts
from plone.app.uuid.utils import uuidToObject

logger = logging.getLogger(PROJECTNAME)


class IPersistentCoverTile(Interface):
    """
    Base interface for tiles that go into the cover object
    """

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
        """ Return a list of content types accepted by the tile or None if all
        types are accepted.
        """

    def get_tile_configuration():
        """
        A method that will return the configuration options for this tile
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


class PersistentCoverTile(tiles.PersistentTile, ESITile):

    implements(IPersistentCoverTile)

    is_configurable = False
    is_editable = True
    is_droppable = True

    def populate_with_object(self, obj):
        if not self.isAllowedToEdit():
            raise Unauthorized(_("You are not allowed to add content to "
                                 "this tile"))

        notify(ObjectModifiedEvent(self))

    def replace_with_objects(self, obj):
        if not self.isAllowedToEdit():
            raise Unauthorized(_("You are not allowed to add content to "
                                 "this tile"))

        notify(ObjectModifiedEvent(self))

    def remove_item(self, uid):
        if not self.isAllowedToEdit():
            raise Unauthorized(_("You are not allowed to remove content of "
                                 "this tile"))

    # XXX: the name of this method is really confusing as it does not deletes
    # the tile; rename it?
    def delete(self):
        """ Remove the persistent data associated with the tile and notify the
        cover object was modified.
        """
        logger.debug('Deleting tile %s', self.id)

        data_mgr = ITileDataManager(self)
        data_mgr.delete()

        # Remove permission data
        permissions = getMultiAdapter((self.context, self.request, self),
                                      ITilesPermissions)
        permissions.delete()

        # Remove configuration data
        configuration = getMultiAdapter((self.context, self.request, self),
                                        ITilesConfigurationScreen)
        configuration.delete()

        notify(ObjectModifiedEvent(self.context))

    def accepted_ct(self):
        """ Return a list of content types accepted by the tile or None if all
        types are accepted.
        """
        return None  # all content types accepted by default

    def get_tile_configuration(self):
        tile_conf_adapter = getMultiAdapter((self.context, self.request, self),
                                            ITilesConfigurationScreen)

        configuration = tile_conf_adapter.get_configuration()

        return configuration

    def _get_tile_field_names(self):
        """Return a list of all field names in the order they were defined.
        """
        tile_type = getUtility(ITileType, name=self.__name__)
        fields = [name for name, obj in getFieldsInOrder(tile_type.schema)]
        return fields

    def _tile_field_is_visible(self, field):
        """Return boolean according to field's visibility; if field name not
        among tile fields, raise AttributeError.
        """
        if field not in self._get_tile_field_names():
            raise AttributeError

        tile_config = self.get_tile_configuration()
        field_config = tile_config[field]
        assert 'visibility' in field_config  # all fields must have visibility

        return field_config['visibility'] == u'on'

    def get_configured_fields(self):
        tileType = queryUtility(ITileType, name=self.__name__)
        conf = self.get_tile_configuration()

        fields = getFieldsInOrder(tileType.schema)

        results = []
        for name, obj in fields:
            if not self.data[name]:
                # If there's no data for this field, ignore it
                continue

            if isinstance(self.data[name], RichTextValue):
                transformer = ITransformer(self.context, None)
                if transformer is not None:
                    content = transformer(self.data[name], 'text/x-html-safe')
            else:
                content = self.data[name]

            field = {'id': name,
                     'content': content,
                     'title': obj.title}  # XXX: object's title?

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
                    field['scale'] = field_conf['imgsize'].split()[0]

                if 'position' in field_conf:
                    field['position'] = field_conf['position']

            results.append(field)

        # XXX: if tile has an image attribute and it's visible, then...
        try:
            if self._tile_field_is_visible('image'):
                self._external_image_configuration(conf, results)
        except AttributeError:
            pass

        return results

    def _external_image_configuration(self, conf, results):
        # XXX: we need to explain better what we're trying to do; we were
        #      including the image field here even if it was set as
        #      non-visible on the configuration screen, so this was raising a
        #      ComponentLookupError on line 409, in scale
        if 'image' in self.data and 'uuid' in self.data and \
                self.data['image'] is None and self.data['uuid']:
            name = 'image'
            scale = 'large'
            if name in conf:
                field_conf = conf[name]
                scale = field_conf['imgsize'].split()[0]
            results.append({'id': name,
                            'scale': scale})

    def setAllowedGroupsForEdit(self, groups):
        permissions = getMultiAdapter((self.context, self.request, self),
                                      ITilesPermissions)
        permissions.set_allowed_edit(groups)

    def getAllowedGroupsForEdit(self):
        permissions = getMultiAdapter((self.context, self.request, self),
                                      ITilesPermissions)
        groups = permissions.get_allowed_edit()

        return groups

    def isAllowedToEdit(self, user=None):
        allowed = True

        pm = getToolByName(self.context, 'portal_membership')

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


# Image scale support for tile images

class AnnotationStorage(BaseAnnotationStorage):
    """ An abstract storage for image scale data using annotations and
        implementing :class:`IImageScaleStorage`. Image data is stored as an
        annotation on the object container, i.e. the image. This is needed
        since not all images are themselves annotatable. """

    @property
    def storage(self):
        tile = self.context
        cover = tile.context
        return IAnnotations(cover).setdefault(
            'plone.tiles.scale.%s' % tile.id,
            PersistentDict())


class ImageScale(BaseImageScale):
    """ view used for rendering image scales """

    def __init__(self, context, request, **info):
        self.context = context
        self.request = request
        self.__dict__.update(**info)
        if self.data is None:
            self.data = getattr(self.context, self.fieldname, None)
        if self.data is None:
            self.data = self.context.data.get(self.fieldname)
        url = self.context.url
        if hasattr(self.data, 'contentType'):
            extension = self.data.contentType.split('/')[-1].lower()
        elif 'mimetype' in info:
            extension = info['mimetype'].split('/')[-1]
        else:
            extension = 'png'  # default images extension
        if 'uid' in info:
            name = info['uid']
        else:
            name = info['fieldname']
        self.__name__ = '%s.%s' % (name, extension)
        self.url = '%s/@@images/%s' % (url, self.__name__)

    def index_html(self):
        """ download the image """
        # validate access
        set_headers(self.data, self.request.response)
        return stream_data(self.data)


class ImageScaling(BaseImageScaling):
    """ view used for generating (and storing) image scales """

    def __init__(self, context, request, **info):
        tile_data = context.data
        if tile_data.get('image') not in (None, True):
            self.context = context
        elif tile_data.get('uuid') is not None:
            self.context = uuidToObject(tile_data.get('uuid'))
        self.request = request

    def publishTraverse(self, request, name):
        """ used for traversal via publisher, i.e. when using as a url """
        stack = request.get('TraversalRequestNameStack')
        image = None
        if stack:
            # field and scale name were given...
            scale = stack.pop()
            image = self.scale(name, scale)             # this is aq-wrapped
        elif '-' in name:
            # we got a uid...
            if '.' in name:
                name, ext = name.rsplit('.', 1)
            storage = AnnotationStorage(self.context)
            info = storage.get(name)
            if info is not None:
                scale_view = ImageScale(self.context, self.request, **info)
                return scale_view.__of__(self.context)
        else:
            # otherwise `name` must refer to a field...
            if '.' in name:
                name, ext = name.rsplit('.', 1)
            value = self.context.data.get(name)
            scale_view = ImageScale(self.context, self.request,
                                    data=value, fieldname=name)
            return scale_view.__of__(self.context)
        if image is not None:
            return image
        raise NotFound(self, name, self.request)

    def create(self, fieldname, direction='thumbnail',
               height=None, width=None, **parameters):
        """ factory for image scales, see `IImageScaleStorage.scale` """
        if not IPersistentCoverTile.providedBy(self.context):
            base_scales = getMultiAdapter((self.context, self.request), name='images')
            return base_scales.create(fieldname, direction, height, width, **parameters)
        orig_value = self.context.data.get(fieldname)
        if orig_value is None:
            return
        if height is None and width is None:
            _, format = orig_value.contentType.split('/', 1)
            return None, format, (orig_value._width, orig_value._height)
        if hasattr(aq_base(orig_value), 'open'):
            orig_data = orig_value.open()
        else:
            orig_data = getattr(aq_base(orig_value), 'data', orig_value)
        if not orig_data:
            return
        try:
            result = scaleImage(orig_data, direction=direction,
                                height=height, width=width, **parameters)
        except (ConflictError, KeyboardInterrupt):
            raise
        except Exception:
            exception('could not scale "%r" of %r',
                      orig_value, self.context.context.absolute_url())
            return
        if result is not None:
            data, format, dimensions = result
            mimetype = 'image/%s' % format.lower()
            value = orig_value.__class__(data, contentType=mimetype,
                                         filename=orig_value.filename)
            value.fieldname = fieldname
            return value, format, dimensions

    def modified(self):
        """ provide a callable to return the modification time of content
            items, so stored image scales can be invalidated """
        if not IPersistentCoverTile.providedBy(self.context):
            base_scales = getMultiAdapter((self.context, self.request), name='images')
            return base_scales.modified()
        mtime = ''
        for k, v in self.context.data.items():
            if INamedImage.providedBy(v):
                mtime += self.context.data.get('%s_mtime' % k, 0)

        return mtime

    def scale(self, fieldname=None, scale=None,
              height=None, width=None, **parameters):
        if not IPersistentCoverTile.providedBy(self.context):
            base_scales = getMultiAdapter((self.context, self.request), name='images')
            try:
                return base_scales.scale(fieldname, scale, height, width, **parameters)
            except AttributeError:
                return
        if fieldname is None:
            fieldname = IPrimaryFieldInfo(self.context).fieldname
        if scale is not None:
            available = self.getAvailableSizes(fieldname)
            if not scale in available:
                return None
            width, height = available[scale]
        storage = AnnotationStorage(self.context, self.modified)
        info = storage.scale(factory=self.create,
                             fieldname=fieldname, height=height, width=width, **parameters)
        if info is not None:
            info['fieldname'] = fieldname
            scale_view = ImageScale(self.context, self.request, **info)
            return scale_view.__of__(self.context)


class PersistentCoverTilePurgePaths(object):
    """Paths to purge for cover tiles
    """

    implements(IPurgePaths)
    adapts(IPersistentCoverTile)

    def __init__(self, context):
        self.context = context

    def getRelativePaths(self):
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, context.request),
                                       name=u'plone_portal_state')
        prefix = context.url.replace(portal_state.portal_url(), '', 1)

        yield prefix
        for _, v in context.data.items():
            if INamedImage.providedBy(v):
                yield "%s/@@images/image" % prefix
                scales = aq_parent(context).unrestrictedTraverse(prefix.strip('/') + '/@@images')
                for size in scales.getAvailableSizes().keys():
                    yield "%s/@@images/%s" % (prefix, size,)

    def getAbsolutePaths(self):
        return []
