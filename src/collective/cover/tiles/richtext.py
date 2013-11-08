# -*- coding: utf-8 -*-

# Basic implementation taken from
# http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.app.textfield import RichText
from plone.app.textfield.interfaces import ITransformer
from plone.app.textfield.value import RichTextValue
from plone.tiles.interfaces import ITileDataManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IRichTextTileData(IPersistentCoverTile):

    text = RichText(title=u'Text')


class RichTextTile(PersistentCoverTile):

    index = ViewPageTemplateFile('templates/richtext.pt')

    is_configurable = True
    short_name = _(u'msg_short_name_richtext', default=u'Rich Text')

    def getText(self):
        """ Return the rich text stored in the tile.
        """
        text = ''
        if self.data['text']:
            text = self.data['text']
            # We expect that the text has a mimeType and an output
            # attribute, but someone may be using a different widget
            # returning a simple unicode, so check that.
            if not isinstance(text, basestring):
                transformer = ITransformer(self.context, None)
                if transformer is not None:
                    text = transformer(text, 'text/x-html-safe')
        return text

    def populate_with_object(self, obj):
        super(RichTextTile, self).populate_with_object(obj)

        if hasattr(obj, 'getRawText'):
            text = obj.getRawText().decode('utf-8')
        else:
            # Probably a dexterity item.  This is already unicode.
            text = obj.text.raw

        value = RichTextValue(raw=text,
                              mimeType='text/x-html-safe',
                              outputMimeType='text/x-html-safe')
        data_mgr = ITileDataManager(self)

        data_mgr.set({'text': value})

    def accepted_ct(self):
        """Return 'Document' as the only content type accepted in the tile."""
        return ['Document']
