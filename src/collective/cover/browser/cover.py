# -*- coding: utf-8 -*-
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IImagingSchema
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.interface import implementer


def get_settings():
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IImagingSchema, prefix="plone", check=False)
    return settings


@implementer(IBlocksTransformEnabled)
class View(BrowserView):

    """Default view, a compose page."""

    index = ViewPageTemplateFile("templates/view.pt")

    def __call__(self):
        # forbid image indexing as scales are volatile
        self.request.RESPONSE.setHeader("X-Robots-Tag", "noimageindex")
        return self.index()


@implementer(IBlocksTransformEnabled)
class Standard(BrowserView):

    """A standard content type like view."""

    index = ViewPageTemplateFile("templates/standard.pt")

    def __call__(self):
        return self.index()


class UpdateTile(BrowserView):

    """Helper browser view to update the tile with Ajax."""

    def setup(self):
        self.tile_id = self.request.form.get("tile-id", None)

    def render(self):
        try:
            tile = self.context.get_tile(self.tile_id)
        except ValueError:
            # requested tile does not exist
            self.request.response.setStatus(400)
            return u""
        return tile()

    def __call__(self):
        self.setup()
        return self.render()


class Helper(BrowserView):
    """Helper view used to retrieve image scales on the namedimage
    configuration widget.
    """

    @staticmethod
    def get_image_scales():
        """List all image scales which are available on the site."""
        settings = get_settings()
        return settings.allowed_sizes
