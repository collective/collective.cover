# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MimetypesRegistry.common import MimeTypeException
from zope import schema
from zope.interface import implementer


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


def get_download_html(url, portal_url, icon, mime_type, size):
    if size < 1024:
        size_str = '{0} bytes'.format(size)
    elif 1024 <= size < 1048576:
        size_str = '{0} kB ({1} bytes)'.format(size / 1024, size)
    else:
        size_str = '{0} MB ({1} bytes)'.format(size / 1048576, size)

    return HTML.format(url, portal_url, icon, mime_type, size_str)


def lookupMime(obj, name):
    """Given an id, return the human representation of mime-type.
    This is a helper funtion to deal with API inconsistencies.
    It's based on a simplified version of the `lookupMime` script
    included in Products.Archetypes `archetypes` skin.
    """
    mtr = api.portal.get_tool('mimetypes_registry')
    try:
        mimetypes = mtr.lookup(name)
    except MimeTypeException:
        return None

    if len(mimetypes):
        return mimetypes[0].name()
    return name


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


@implementer(IFileTile)
class FileTile(PersistentCoverTile):

    index = ViewPageTemplateFile('templates/file.pt')

    is_configurable = False  # TODO: make the tile configurable
    is_editable = True
    is_droppable = True
    short_name = _(u'msg_short_name_file', default=u'File')

    def get_content_type(self, obj):
        """Return MIME type for both, Archetypes and Dexterity items."""
        try:
            return obj.getContentType()  # Archetypes
        except AttributeError:
            return obj.file.contentType  # Dexterity

    def getBestIcon(self, obj):
        """Find most specific icon for a Dexterity object.

        This is a simplified version of the `getBestIcon` script
        included in Products.Archetypes `archetypes` skin.
        Should be probably included in plone.app.contenttypes.
        """
        mtr = api.portal.get_tool('mimetypes_registry')
        content_type = obj.file.contentType

        try:
            lookup = mtr.lookup(content_type)
        except MimeTypeException:
            return None

        if lookup:
            mti = lookup[0]
            return mti.icon_path

        return None

    def download_widget(self):
        """ Returns a download link for the file associated with the tile.
        """
        obj = uuidToObject(self.data['uuid'])
        if obj:
            url = obj.absolute_url()
            portal_url = obj.portal_url()
            content_type = self.get_content_type(obj)

            try:
                # Archetypes
                icon = obj.getBestIcon()
                mime = obj.lookupMime(content_type)
                size = obj.get_size()
            except AttributeError:
                # Dexterity
                icon = self.getBestIcon(obj)
                mime = lookupMime(obj, content_type)
                size = obj.file.size

            return get_download_html(url, portal_url, icon, mime, size)

    def is_empty(self):
        return not (self.data.get('title', None) or
                    self.data.get('description', None) or
                    self.data.get('uuid', None))

    def populate_with_object(self, obj):
        super(FileTile, self).populate_with_object(obj)  # check permissions

        if obj.portal_type not in self.accepted_ct():
            return
        data = {
            'title': safe_unicode(obj.Title()),
            'description': safe_unicode(obj.Description()),
            'download': True,
            'uuid': IUUID(obj),
        }
        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    def accepted_ct(self):
        """Return 'File' as the only content type accepted in the tile."""
        return ['File']
