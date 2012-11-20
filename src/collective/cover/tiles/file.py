# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.namedfile.field import NamedBlobImage as NamedImage
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


class IFileTile(IPersistentCoverTile):

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
        readonly=True,  # this field can not be edited or configured
    )

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


class FileTile(PersistentCoverTile):

    implements(IFileTile)

    index = ViewPageTemplateFile('templates/file.pt')

    is_configurable = False  # TODO: make the tile configurable
    is_editable = True
    is_droppable = True

    # XXX: initialize tile? how?
    #def __init__(self, context, request):
    #    super(PersistentCoverTile, self).__init__(context, request)

        #data_mgr = ITileDataManager(self)
        #data_mgr.set({'title': '', 'description': '', 'image': '', 'download': '', 'uuid': ''})

    def get_title(self):
        """ Returns the title stored in the tile.
        """
        return self.data['title']

    def get_description(self):
        """ Returns the description stored in the tile.
        """
        return self.data['description']

    def get_image(self):
        """ Returns the image stored in the tile.
        """
        return self.data['image']

    def download_widget(self):
        """ Returns a download link for the file associated with the tile.
        """
        obj = uuidToObject(self.data['uuid'])
        if obj:
            url = obj.absolute_url()
            icon = obj.getBestIcon()
            portal_url = obj.portal_url()
            mime = obj.lookupMime(obj.getField('file').getContentType(obj))
            size = obj.get_size()
            return get_download_html(url, portal_url, icon, mime, size)

    def get_date(self):
        """ Returns the date of the file associated with the tile.
        """
        # TODO: support selection of which date we want to display
        obj = uuidToObject(self.data['uuid'])
        if obj:
            return obj.Date()

    def is_empty(self):
        return not(self.data.get('title') or
                   self.data.get('description') or
                   self.data.get('image') or
                   self.data.get('uuid'))

    def populate_with_object(self, obj):
        super(FileTile, self).populate_with_object(obj)  # check permissions

        title = obj.Title() if hasattr(obj, 'Title') else None
        description = obj.Description() if hasattr(obj, 'Description') else None
        uuid = IUUID(obj, None)

        data_mgr = ITileDataManager(self)
        data_mgr.set({'title': title,
                      'description': description,
                      'download': True,
                      'uuid': uuid,
                      })

    def accepted_ct(self):
        """ Return a list of content types accepted by the tile.
        """
        return ['File']
