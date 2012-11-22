# -*- coding: utf-8 -*-

# Basic implementation taken from
# http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts

from plone.app.textfield import RichText
from plone.app.textfield.interfaces import ITransformer
from plone.app.textfield.value import RichTextValue

from plone.tiles.interfaces import ITileDataManager

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile


class IRichTextTileData(IPersistentCoverTile):

    text = RichText(title=u'Text')


class RichTextTile(PersistentCoverTile):

    index = ViewPageTemplateFile("templates/richtext.pt")

    is_configurable = True

    def getText(self):
        """ Return the rich text stored in the tile.
        """
        text = ''
        if self.data['text']:
            transformer = ITransformer(self.context, None)
            if transformer is not None:
                text = transformer(self.data['text'], 'text/x-html-safe')
        return text

    def populate_with_object(self, obj):
        super(RichTextTile, self).populate_with_object(obj)

        text = obj.getRawText().decode('utf-8')
        value = RichTextValue(raw=text,
                              mimeType='text/x-html-safe',
                              outputMimeType='text/x-html-safe')
        data_mgr = ITileDataManager(self)

        data_mgr.set({'text': value})

    def accepted_ct(self):
        """ Return a list of content types accepted by the tile.
        """
        return ['Document']
