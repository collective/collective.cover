# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone import api
from plone.namedfile import field
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_hasattr
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implementer


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

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


@implementer(IBannerTile)
class BannerTile(PersistentCoverTile):

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

        if obj.portal_type == 'Link':
            try:
                remote_url = obj.getRemoteUrl()  # Archetypes
            except AttributeError:
                remote_url = obj.remoteUrl  # Dexterity
        else:
            # Get object URL
            # For Image and File objects (or any other in typesUseViewActionInListings)
            # we must add a /view to prevent the download of the file
            obj_url = obj.absolute_url_path()
            props = api.portal.get_tool('portal_properties')
            stp = props.site_properties
            view_action_types = stp.getProperty('typesUseViewActionInListings', ())

            if safe_hasattr(obj, 'portal_type') and obj.portal_type in view_action_types:
                obj_url += '/view'

            remote_url = obj_url

        image = self.get_image_data(obj)
        if image:
            # clear scales if new image is getting saved
            self.clear_scales()

        obj = aq_base(obj)  # avoid acquisition
        title = safe_unicode(obj.Title())
        description = safe_unicode(obj.Description())

        data_mgr = ITileDataManager(self)
        data_mgr.set({
            'title': title,
            'description': description,
            'uuid': IUUID(obj),
            'image': image,
            'remote_url': remote_url,
        })

    def getRemoteUrl(self):
        return self.data.get('remote_url', None)

    @property
    def is_empty(self):
        return not(self.data.get('title') or self.has_image or self.getRemoteUrl())

    @property
    def css_class(self):
        tile_conf = self.get_tile_configuration()
        image_conf = tile_conf.get('image', None)
        if image_conf:
            css_class = image_conf['position']
            return css_class

    @property
    def htmltag(self):
        tile_conf = self.get_tile_configuration()
        title_conf = tile_conf.get('title', None)
        if title_conf:
            htmltag = title_conf['htmltag']
            return htmltag

    @property
    def alt(self):
        """Return the alt attribute for the image."""
        return self.data.get('description') or self.data.get('title')
