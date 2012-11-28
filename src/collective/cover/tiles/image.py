# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.namedfile.file import NamedBlobImage

from plone.tiles.interfaces import ITileDataManager

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile


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

        data_mgr = ITileDataManager(self)

        data_mgr.set({'image': NamedBlobImage(obj.getImage().data)})

    def accepted_ct(self):
        """ Return a list of content types accepted by the tile.
        """
        valid_ct = ['Image']
        return valid_ct
