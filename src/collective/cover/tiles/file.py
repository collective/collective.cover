# -*- coding: utf-8 -*-

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import safe_unicode
from zope import schema
from zope.interface import implements

HTML = """
    <a href="{0}/at_download/file">
      <img src="{1}/{2}" alt="">
         Download file
    </a>
    <span class="discreet">
      &#8212;
      {3},
      {4}
    </span>
"""


# XXX: refactor this to make it easier to test
def get_download_html(url, portal_url, icon, mime_type, size):
    if size < 1024:
        size_str = '{0} bytes'.format(size)
    elif size >= 1024 and size < 1048576:
        size_str = '{0} kB ({1} bytes)'.format(size / 1024, size)
    else:
        size_str = '{0} MB ({1} bytes)'.format(size / 1048576, size)

    return HTML.format(url, portal_url, icon, mime_type, size_str)


class IFileTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Description'),
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
    short_name = _(u'msg_short_name_file', default=u'File')

    # XXX: refactor this to make it easier to test
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

    def is_empty(self):
        return not (self.data.get('title', None) or
                    self.data.get('description', None) or
                    self.data.get('uuid', None))

    def populate_with_object(self, obj):
        super(FileTile, self).populate_with_object(obj)  # check permissions

        if obj.portal_type in self.accepted_ct():
            title = safe_unicode(obj.Title())
            description = safe_unicode(obj.Description())
            uuid = IUUID(obj)

            data_mgr = ITileDataManager(self)
            data_mgr.set({'title': title,
                          'description': description,
                          'download': True,
                          'uuid': uuid,
                          })

    def accepted_ct(self):
        """Return 'File' as the only content type accepted in the tile."""
        return ['File']
