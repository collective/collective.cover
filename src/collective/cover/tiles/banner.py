# -*- coding: utf-8 -*-

from Acquisition import aq_base
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.namedfile import field
from plone.namedfile import NamedBlobImage
from plone.tiles.interfaces import ITileDataManager
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import safe_unicode
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
    short_name = _(u'msg_short_name_banner', default=u'Banner')

    def populate_with_object(self, obj):
        """Tile can be populated with any content type with image
        or getImage attribute; in this case we're not
        going to take care of any modification of the original object; we just
        copy the data to the tile and deal with it.
        """
        if obj.portal_type not in self.accepted_ct():
            return

        super(BannerTile, self).populate_with_object(obj)  # check permissions

        if hasattr(obj, 'getRemoteUrl'):
            remote_url = obj.getRemoteUrl()
        else:
            # Get object URL
            # For Image and File objects (or any other in typesUseViewActionInListings)
            # we must add a /view to prevent the download of the file
            obj_url = obj.absolute_url_path()
            props = getToolByName(obj, 'portal_properties')
            stp = props.site_properties
            view_action_types = stp.getProperty('typesUseViewActionInListings', ())

            if hasattr(obj, 'portal_type') and obj.portal_type in view_action_types:
                obj_url += '/view'

            remote_url = obj_url

        image = None
        # if has image, store a copy of its data
        if self._has_image_field(obj) and self._field_is_visible('image'):
            scales = obj.restrictedTraverse('@@images')
            image = scales.scale('image', None)

        if image is not None and image != '':
            image = NamedBlobImage(image.data)

        obj = aq_base(obj)  # avoid acquisition
        title = safe_unicode(obj.Title())

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
