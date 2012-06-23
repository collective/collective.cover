# -*- coding: utf-8 -*-

# Basic implementation taken from
# http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts

from zope.interface import Interface
from zope.component import adapts
from zope import schema
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone import tiles
from plone.app.textfield import RichText
from plone.app.textfield.interfaces import ITransformer
from plone.namedfile.field import NamedImage

from plone.tiles.interfaces import ITileDataManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.namedfile.utils import set_headers, stream_data

class IBasicTileData(Interface):

    title = schema.TextLine(title=u'Title',
                            required=False,
                            )
    description = schema.Text(title=u'Descrition',
                              required=False,
                              )
    image = NamedImage(title=u'Image',
                       required=False,
                       )

    def getTitle():
        """
        A method to return the title stored in the tile
        """

    def getDescription():
        """
        A method to return the description stored in the tile
        """

    def getImage():
        """
        A method to return the image stored in the tile
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


class BasicTile(tiles.PersistentTile):

    index = ViewPageTemplateFile("templates/basic.pt")

    def getText(self):
        text = ''
        if self.data['text']:
            transformer = ITransformer(self.context, None)
            if transformer is not None:
                text = transformer(self.data['text'], 'text/x-html-safe')
        return text

    def getTitle(self):
        return self.data['title']

    def getDescription(self):
        return self.data['description']

    def image_tag(self):
        return '<img src="%s/@@image" />' % self.url

    def is_empty(self):
        return not(self.data['title'] or \
                   self.data['description'] or \
                   self.data['image'])
        
    def populate_with_object(self, obj):
        data_mgr = ITileDataManager(self)

        data_mgr.set({'title': obj.Title(),
                      'description': obj.Description(),
                      })

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = ['Document',]
        return valid_ct


class ImageView(BrowserView):
    """ view used for rendering image"""

    def __call__(self):
        data = self.context.data['image']
        if data:
            set_headers(data, self.request.response)
            return stream_data(data)
