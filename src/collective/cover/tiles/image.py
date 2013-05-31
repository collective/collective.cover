# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.memoize.instance import memoizedproperty
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.deprecation import deprecated
from zope.interface import implements


class IImageTile(IPersistentCoverTile):

    image = NamedImage(
        title=_(u'Image'),
        required=False,
    )

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


class ImageTile(PersistentCoverTile):

    implements(IImageTile)

    index = ViewPageTemplateFile('templates/image.pt')

    is_configurable = True

    @memoizedproperty
    def brain(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        uuid = self.data.get('uuid')
        result = catalog(UID=uuid) if uuid is not None else []
        assert len(result) <= 1
        return result[0] if result else None

    def Date(self):
        """ Return the date of publication of the original object; if it has
        not been published yet, it will return its modification date.
        """
        if self.brain is not None:
            return self.brain.Date

    def is_empty(self):
        return self.brain is None and \
            not [i for i in self.data.values() if i]

    def getURL(self):
        """ Return the URL of the original object.
        """
        if self.brain is not None:
            return self.brain.getURL()

    def description(self):
        """ Return the description of the original image
        """
        if self.brain is not None:
            return self.brain.Description

    def title(self):
        """ Return the title of the original image
        """
        if self.brain is not None:
            return self.brain.Title

    def populate_with_object(self, obj):
        # check permissions
        super(ImageTile, self).populate_with_object(obj)

        data = {
            'uuid': IUUID(obj, None),  # XXX: can we get None here? see below
        }

        # TODO: if a Dexterity object does not have the IReferenceable
        # behaviour enable then it will not work here
        # we need to figure out how to enforce the use of
        # plone.app.referenceablebehavior
        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    def accepted_ct(self):
        return ['Image']


deprecated(
    'IImageTile',
    "Image Tile is deprecated use Banner Tile instead. Image Tile will be "
    "removed in collective.cover 1.0a5.")
