# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
from collective.cover.utils import get_types_use_view_action_in_listings
from plone.autoform import directives as form
from plone.namedfile import field
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implementer


class IBannerTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    form.omitted(IDefaultConfigureForm, 'remote_url')
    remote_url = schema.URI(
        title=_(u'label_remote_url', default=u'URL'),
        description=_(
            u'help_remote_url', default=u'Use absolute links only.'),
        required=False,
    )

    image = field.NamedBlobImage(
        title=_(u'Image'),
        required=False,
    )

    form.omitted(IDefaultConfigureForm, 'alt_text')
    alt_text = schema.TextLine(
        title=_(
            u'label_alt_text',
            default=u'Alternative Text'),
        description=_(
            u'help_alt_text',
            default=u'Provides a textual alternative to non-text content in web pages.'),  # noqa E501
        required=False,
    )

    uuid = schema.TextLine(  # FIXME: this must be schema.ASCIILine()
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
            remote_url = obj.absolute_url()
            if obj.portal_type in get_types_use_view_action_in_listings():
                remote_url += '/view'

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
            # FIXME: https://github.com/collective/collective.cover/issues/778
            'alt_text': description or title,
            'remote_url': remote_url,
        })

    def getRemoteUrl(self):
        """Return the remote URL field."""
        return self.data.get('remote_url') or u''  # deal with None values

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
        """Return alternative text dealing with form init issues."""
        alt_text = self.data['alt_text']
        return alt_text if alt_text is not None else u''
