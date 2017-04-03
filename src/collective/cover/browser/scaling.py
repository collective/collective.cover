# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.cover.tiles.base import IPersistentCoverTile
from persistent.dict import PersistentDict
from plone.app.uuid.utils import uuidToObject
from plone.namedfile.interfaces import INamedImage
from plone.namedfile.scaling import ImageScale as BaseImageScale
from plone.namedfile.scaling import ImageScaling as BaseImageScaling
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.scale.scale import scaleImage
from plone.scale.storage import AnnotationStorage as BaseAnnotationStorage
from Products.CMFPlone.utils import safe_hasattr
from ZODB.POSException import ConflictError
from zope.annotation import IAnnotations
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import NotFound

import logging


# XXX: these are views, we should move it away from this module
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
            'plone.tiles.scale.{0}'.format(tile.id), PersistentDict())


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
        if safe_hasattr(self.data, 'contentType'):
            extension = self.data.contentType.split('/')[-1].lower()
        elif 'mimetype' in info:
            extension = info['mimetype'].split('/')[-1]
        else:
            extension = 'png'  # default images extension
        if 'uid' in info:
            name = info['uid']
        else:
            name = info['fieldname']
        self.__name__ = '{0}.{1}'.format(name, extension)
        self.url = '{0}/@@images/{1}'.format(url, self.__name__)

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
            # we got a uuid...
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
            base_scales = queryMultiAdapter((self.context, self.request),
                                            name='images', default=None)
            return base_scales and base_scales.create(fieldname,
                                                      direction,
                                                      height,
                                                      width,
                                                      **parameters)
        orig_value = self.context.data.get(fieldname)
        if orig_value is None:
            return
        if height is None and width is None:
            _, format = orig_value.contentType.split('/', 1)
            return None, format, (orig_value._width, orig_value._height)
        if safe_hasattr(aq_base(orig_value), 'open'):
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
        except Exception:  # FIXME: B901 blind except: statement
            logging.exception(
                'could not scale "{0}" of {1}'.format(
                    repr(orig_value),
                    repr(self.context.context.absolute_url())))
            return
        if result is not None:
            data, format_, dimensions = result
            mimetype = 'image/' + format_.lower()
            value = orig_value.__class__(data, contentType=mimetype,
                                         filename=orig_value.filename)
            value.fieldname = fieldname
            return value, format_, dimensions

    def modified(self):
        """ provide a callable to return the modification time of content
            items, so stored image scales can be invalidated """
        if not IPersistentCoverTile.providedBy(self.context):
            base_scales = queryMultiAdapter((self.context, self.request),
                                            name='images',
                                            default=None)
            return base_scales and base_scales.modified()
        mtime = None
        for k, v in self.context.data.items():
            if INamedImage.providedBy(v):
                mtime = self.context.data.get('{0}_mtime'.format(k), None)

        return mtime

    def scale(self, fieldname=None, scale=None,
              height=None, width=None, **parameters):
        if not IPersistentCoverTile.providedBy(self.context):
            base_scales = queryMultiAdapter((self.context, self.request),
                                            name='images',
                                            default=None)
            if base_scales:
                try:
                    scale = base_scales.scale(fieldname,
                                              scale,
                                              height,
                                              width,
                                              **parameters)
                except AttributeError:
                    scale = None
                return scale
            else:
                return None
        if fieldname is None:
            fieldname = IPrimaryFieldInfo(self.context).fieldname
        if scale is not None:
            available = self.getAvailableSizes(fieldname)
            if scale not in available:
                return None
            width, height = available[scale]
        storage = AnnotationStorage(self.context, self.modified)
        info = storage.scale(factory=self.create,
                             fieldname=fieldname,
                             height=height,
                             width=width,
                             **parameters)
        if info is not None:
            info['fieldname'] = fieldname
            scale_view = ImageScale(self.context, self.request, **info)
            return scale_view.__of__(self.context)
