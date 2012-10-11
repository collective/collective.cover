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

    def getText():
        """
        A method to return the rich text stored in the tile
        """

    def populate_with_object(obj):
        """
        This method will take a CT object as parameter, and it will store the
        content of the 'text' field into the tile.
        """

    def delete():
        """
        This method removes the persistent data created for this tile
        """


class RichTextTile(PersistentCoverTile):

    index = ViewPageTemplateFile("templates/richtext.pt")

    is_configurable = True

    def getText(self):
        text = ''
        if self.data['text']:
            transformer = ITransformer(self.context, None)
            if transformer is not None:
                text = transformer(self.data['text'], 'text/x-html-safe')
        return text

    #def __ac_local_roles__(self):
        #import pdb;pdb.set_trace()

    def populate_with_object(self, obj):
        super(RichTextTile, self).populate_with_object(obj)

        text = obj.getRawText().decode('utf-8')
        value = RichTextValue(raw=text,
                              mimeType='text/x-html-safe',
                              outputMimeType='text/x-html-safe')
        data_mgr = ITileDataManager(self)

        data_mgr.set({'text': value})

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = ['Document', ]
        return valid_ct
