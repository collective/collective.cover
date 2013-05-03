# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from collective.cover import _
from collective.cover.tiles.base import AnnotationStorage
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.namedfile.file import NamedBlobImage as NamedImageFile
from plone.scale.storage import AnnotationStorage as BaseAnnotationStorage
from plone.tiles.interfaces import ITileDataManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter
from zope.interface import implements

import time


class IImageTile(IPersistentCoverTile):

    image = NamedImage(
        title=_(u'Image'),
        required=False,
    )


class ImageTile(PersistentCoverTile):

    implements(IImageTile)

    index = ViewPageTemplateFile('templates/image.pt')

    is_configurable = True

    def is_empty(self):
        return not(self.data.get('image'))

    def populate_with_object(self, obj):
        # check permissions
        super(ImageTile, self).populate_with_object(obj)

        data = {}
        obj = aq_inner(obj)
        try:
            scales = queryMultiAdapter((obj, self.request), name="images")
            data['image'] = NamedImageFile(str(scales.scale('image').data))
        except AttributeError:
            pass
        data_mgr = ITileDataManager(self)
        data_mgr.set(data)
        tile_storage = AnnotationStorage(self)
        obj_storage = BaseAnnotationStorage(obj)
        for k, v in obj_storage.items():
            tile_storage.storage[k] = v
            tile_storage.storage[k]['modified'] = '%f' % time.time()
            scale_data = obj_storage.storage[k]['data'].open().read()
            tile_storage.storage[k]['data'] = NamedImageFile(str(scale_data))

    def accepted_ct(self):
        """ Return a list of content types accepted by the tile.
        """
        valid_ct = ['Image']
        return valid_ct
