# -*- coding: utf-8 -*-

from Acquisition import aq_base
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.namedfile import field
from plone.namedfile import NamedBlobImage
from plone.tiles.interfaces import ITileDataManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements


class IBannerTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    image = field.NamedBlobImage(
        title=_(u'Image'),
        required=False,
    )

    remote_url = schema.TextLine(
        title=_(u'URL'),
        required=False,
    )


class BannerTile(PersistentCoverTile):
    implements(IBannerTile)

    index = ViewPageTemplateFile('templates/banner.pt')
    is_configurable = True
    is_editable = True
    is_droppable = True

    def accepted_ct(self):
        return ['Image', 'Link']

    def populate_with_object(self, obj):
        """Tile can be populated with images and links; in this case we're not
        going to take care of any modification of the original object; we just
        copy the data to the tile and deal with it.
        """
        if obj.portal_type not in self.accepted_ct():
            return

        super(BannerTile, self).populate_with_object(obj)  # check permissions
        obj = aq_base(obj)  # avoid acquisition
        title = obj.Title()
        # if image, store a copy of its data
        if obj.portal_type == 'Image':
            image = NamedBlobImage(obj.getImage().data)
        else:
            image = None
        remote_url = obj.getRemoteUrl() if obj.portal_type == 'Link' else None

        data_mgr = ITileDataManager(self)
        data_mgr.set({
            'title': title,
            'image': image,
            'remote_url': remote_url,
        })

    def Title(self):
        return self.data.get('title', None)

    @property
    def has_image(self):
        return self.data.get('image', None) is not None

    def getRemoteUrl(self):
        return self.data.get('remote_url', None)

    @property
    def is_empty(self):
        return not (self.Title() or self.has_image or self.getRemoteUrl())

    @property
    def css_class(self):
        tile_conf = self.get_tile_configuration()
        image_conf = tile_conf.get('image', None)
        if image_conf:
            css_class = image_conf['position']
            return css_class

    @property
    def scale(self):
        tile_conf = self.get_tile_configuration()
        image_conf = tile_conf.get('image', None)
        if image_conf:
            scale = image_conf['imgsize']
            # scale string is something like: 'mini 200:200'
            return scale.split(' ')[0]  # we need the name only: 'mini'

    @property
    def htmltag(self):
        tile_conf = self.get_tile_configuration()
        title_conf = tile_conf.get('title', None)
        if title_conf:
            htmltag = title_conf['htmltag']
            return htmltag
