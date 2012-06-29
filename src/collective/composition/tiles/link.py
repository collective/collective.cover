# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.namedfile.interfaces import HAVE_BLOBS
from plone.namedfile.field import NamedImage
if HAVE_BLOBS:
    from plone.namedfile.field import NamedBlobImage as NamedImage

from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID

from plone.app.uuid.utils import uuidToObject

from collective.composition import _
from collective.composition.tiles.base import IPersistentCompositionTile
from collective.composition.tiles.base import PersistentCompositionTile


class ILinkTile(IPersistentCompositionTile):

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

    url = schema.TextLine(
        title=_(u'Link'),
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

    def get_url():
        """ Returns the URL stored in the tile.
        """

    def populate_with_object(obj):
        """ Takes a File object as parameter, and it will store the content of
        its fields into the tile.
        """

    def delete():
        """ Removes the persistent data created for the tile.
        """


class LinkTile(PersistentCompositionTile):

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

    # XXX: can we do this without waking the object up?
    def get_url(self):
        # TODO: we must support be able to select which date we want to
        # display
        obj = uuidToObject(self.data['url'])
        if obj:
            return obj.Date()

    def is_empty(self):
        return not(self.data['title'] or \
                   self.data['description'] or \
                   self.data['image'] or \
                   self.data['link'] or \
                   self.data['uuid'])

    def populate_with_object(self, obj):
        # check permissions
        super(LinkTile, self).populate_with_object(obj)

        title = getattr(obj, 'title', None)
        # FIXME: this is not getting the description, why?
        description = getattr(obj, 'description', None)
        url = getattr(obj, 'link', None)
        uuid = IUUID(obj, None)

        data_mgr = ITileDataManager(self)
        data_mgr.set({'title': title,
                      'description': description,
                      'url': url,
                      'uuid': uuid,
                      })

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = ['Link']
        return valid_ct
