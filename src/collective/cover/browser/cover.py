# -*- coding: utf-8 -*-
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


@implementer(IBlocksTransformEnabled)
class View(BrowserView):

    """Default view, a compose page."""

    index = ViewPageTemplateFile('templates/view.pt')

    def __call__(self):
        # forbid image indexing as scales are volatile
        self.request.RESPONSE.setHeader('X-Robots-Tag', 'noimageindex')
        return self.index()


@implementer(IBlocksTransformEnabled)
class Standard(BrowserView):

    """A standard content type like view."""

    index = ViewPageTemplateFile('templates/standard.pt')

    def __call__(self):
        return self.index()


class UpdateTile(BrowserView):

    """Helper browser view to update the tile with Ajax."""

    def setup(self):
        self.tile_id = self.request.form.get('tile-id', None)

    def render(self):
        try:
            tile = self.context.get_tile(self.tile_id)
        except ValueError:
            # requested tile does not exist
            self.request.response.setStatus(400)
            return u''
        return tile()

    def __call__(self):
        self.setup()
        return self.render()
