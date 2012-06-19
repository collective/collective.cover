# -*- coding: utf-8 -*-

# Basic implementation taken from
# http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts

from zope.interface import Interface

from plone import tiles
from plone.app.textfield import RichText
from plone.app.textfield.interfaces import ITransformer

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IRichTextTileData(Interface):

    text = RichText(title=u'Text')


class RichTextTile(tiles.PersistentTile):

    index = ViewPageTemplateFile("templates/richtext.pt")

    def getText(self):
        text = ''
        if self.data['text']:
            transformer = ITransformer(self.context, None)
            if transformer is not None:
                text = transformer(self.data['text'], 'text/x-html-safe')
        return text

    #def __ac_local_roles__(self):
        #import pdb;pdb.set_trace()
