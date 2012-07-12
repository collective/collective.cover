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


class ILinkTile(IPersistentCoverTile):

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

    remote_url = schema.TextLine(
        title=_(u'URL'),
        required=False,
        )

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,  # the field can not be edited or configured
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

    def get_remote_url():
        """ Returns the URL stored in the tile.
        """

    def populate_with_object(obj):
        """ Takes a File object as parameter, and it will store the content of
        its fields into the tile.
        """

    def delete():
        """ Removes the persistent data created for the tile.
        """


class LinkTile(PersistentCoverTile):

    implements(ILinkTile)

    index = ViewPageTemplateFile('templates/link.pt')

    # TODO: make it configurable
    is_configurable = False

    def get_title(self):
        return self.data['title']

    def get_description(self):
        return self.data['description']

    def get_image(self):
        return self.data['image']

    # XXX: can we do this without waking the object up?
    def get_date(self):
        # TODO: we must support be able to select which date we want to
        # display
        obj = uuidToObject(self.data['uuid'])
        if obj:
            return obj.Date()

    def get_remote_url(self):
        return self.data['remote_url']

    def is_empty(self):
        return not(self.data['title'] or \
                   self.data['description'] or \
                   self.data['image'] or \
                   self.data['remote_url'] or \
                   self.data['uuid'])

    def populate_with_object(self, obj):
        # check permissions
        super(LinkTile, self).populate_with_object(obj)

        title = obj.Title()
        description = obj.Description()
        remote_url = obj.getRemoteUrl()
        uuid = IUUID(obj, None)

        data_mgr = ITileDataManager(self)
        data_mgr.set({'title': title,
                      'description': description,
                      'remote_url': remote_url,
                      'uuid': uuid,
                      })

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = ['Link']
        return valid_ct
