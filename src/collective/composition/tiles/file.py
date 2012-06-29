# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID

from plone.app.uuid.utils import uuidToObject

from collective.composition import _
from collective.composition.tiles.base import IPersistentCompositionTile
from collective.composition.tiles.base import PersistentCompositionTile

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


class IFileTile(IPersistentCompositionTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
        )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        )

    image = NamedImage(
        title=_(u'Image'),
        required=False,
        )

    download = schema.TextLine(
        title=_(u'Download link'),
        required=False,
        readonly=True,  # the field can not be edited or configured
        )

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
        )

    def get_title():
        """ Returns the title stored in the tile.
        """

    def get_description():
        """ Returns the description stored in the tile.
        """

    def get_image():
        """ Returns the image stored in the tile.
        """

    def download_widget():
        """ Returns a download link for the file associated with the tile.
        """

    def get_date():
        """ Returns the date of the file associated with the tile.
        """

    def populate_with_object(obj):
        """ Takes a File object as parameter, and it will store the content of
        its fields into the tile.
        """

    def delete():
        """ Removes the persistent data created for the tile.
        """


class FileTile(PersistentCompositionTile):

    implements(IFileTile)

    index = ViewPageTemplateFile('templates/file.pt')

    # TODO: make it configurable
    is_configurable = False

    def get_title(self):
        return self.data['title']

    def get_description(self):
        return self.data['description']

    def get_image(self):
        return self.data['image']

    # XXX: can we do this without waking the object up?
    def download_widget(self):
        obj = uuidToObject(self.data['uuid'])
        if obj:
            url = obj.absolute_url()
            icon = obj.getBestIcon()
            portal_url = obj.portal_url()
            mime = obj.lookupMime(obj.getField('file').getContentType(obj))
            size = obj.get_size()
            return get_download_html(url, portal_url, icon, mime, size)

    # XXX: can we do this without waking the object up?
    def get_date(self):
        # TODO: we must support be able to select which date we want to
        # display
        obj = uuidToObject(self.data['uuid'])
        if obj:
            return obj.Date()

    def is_empty(self):
        return not(self.data['title'] or \
                   self.data['description'] or \
                   self.data['image'] or \
                   self.data['uuid'])

    def populate_with_object(self, obj):
        # check permissions
        super(FileTile, self).populate_with_object(obj)

        title = getattr(obj, 'title', None)
        # FIXME: this is not getting the description, why?
        description = getattr(obj, 'description', None)
        uuid = IUUID(obj, None)

        data_mgr = ITileDataManager(self)
        data_mgr.set({'title': title,
                      'description': description,
                      'download': True,
                      'uuid': uuid,
                      })

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = ['File']
        return valid_ct
