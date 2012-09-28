# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.namedfile.field import NamedBlobImage as NamedImage

from plone.namedfile.file import NamedBlobImage

from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID

from plone.app.uuid.utils import uuidToObject

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile

HTML = """
    <a href="%s/at_download/file">
      <img src="%s/%s" alt="">
         Download file
    </a>
    <span class="discreet">
      &#8212;
      %s,
      %s
    </span>
"""


def get_download_html(url, portal_url, icon, mime_type, size):
    if size < 1024:
        size_str = '%s bytes' % size
    elif size >= 1024 and size <= 1048576:
        size_str = '%s kB (%s bytes)' % (size / 1024, size)
    else:
        size_str = '%s MB (%s bytes)' % (size / 1048576, size)

    return HTML % (url, portal_url, icon, mime_type, size_str)


class IImageTile(IPersistentCoverTile):

    image = NamedImage(
        title=_(u'Image'),
        required=False,
        )

    def get_image():
        """ Returns the image stored in the tile.
        """

    def is_empty():
        """ Returns True if the tile has no content
        """

    def populate_with_object(obj):
        """ Takes an Image object as parameter, and it will store the content of
        its fields into the tile.
        """


class ImageTile(PersistentCoverTile):

    implements(IImageTile)

    index = ViewPageTemplateFile('templates/image.pt')

    is_configurable = True

    def get_image(self):
        return self.data['image']

    def is_empty(self):
        return not(self.data['image'])

    def populate_with_object(self, obj):
        # check permissions
        super(ImageTile, self).populate_with_object(obj)

        data_mgr = ITileDataManager(self)

        data_mgr.set({'image': NamedBlobImage(obj.getImage().data)})

    def accepted_ct(self):
        valid_ct = ['Image']
        return valid_ct
