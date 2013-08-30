# -*- coding: utf-8 -*-

from persistent.dict import PersistentDict
from plone.namedfile.interfaces import INamedBlobImageField
from plone.tiles.interfaces import ITileType
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface
from zope.schema import getFieldNamesInOrder
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import ITextLine


ANNOTATIONS_KEY_PREFIX = u'plone.tiles.configuration'


class ITilesConfigurationScreen(Interface):

    def _set_default_configuration():
        """Return a default configuration based on fields defined on the
        schema; all fields must have, at least, the following attributes:

        visibility: (u'on', u'off')
            is the field visible? defaults to u'on'
            XXX: this could be a boolean in the future
        order: (u'1', u'2', ...)
            in which order we are going to display the field?
            XXX: until we fix the UI, we must start with 1 instead of 0
                 because is most intuitive for end users

        the following attribute is available only in TextLine fields:

        htmltag: (u'h1', u'h2', ...)
            defaults to u'h2'
            XXX: this name is a bad one, but I have no proposal for now

        the following attributes are available only in NamedImage fields:

        position: (u'inline', u'left', u'right')
            defaults to u'left'
            XXX: this should be named 'alignment' probably
        imgsize: (any of the available sizes for scaled down images)
            defaults to u'mini 200:200' or first available size
            XXX: this should be named 'scale' probably

        final result will be something like this:

        {'date': {'order': u'3', 'visibility': u'on'},
         'description': {'order': u'1', 'visibility': u'on'},
         'image': {'imgsize': u'mini 200:200',
                   'order': u'2',
                   'position': u'left',
                   'visibility': u'on'},
         'subjects': {'order': u'4', 'visibility': u'on'},
         'title': {'htmltag': u'h2', 'order': u'0', 'visibility': u'on'},
         'uuid': {'htmltag': u'h2', 'order': u'5', 'visibility': u'on'}}

        obviously some of the fields are not ment to be displayed, but that's
        another story.
        """

    def get_configuration():
        """
        Get the configuration for a given tile
        """

    def set_configuration(configuration):
        """
        Set the configuration for a given tile
        """

    def delete():
        """
        Remove configurations for a given tile
        """


class TilesConfigurationScreen(object):
    """
    An adapter that will provide the configuration screens functionality
    """

    implements(ITilesConfigurationScreen)

    def __init__(self, context, request, tile):
        self.context = context
        self.request = request
        self.tile = tile
        self.annotations = IAnnotations(self.context)
        self.key = '{0}.{1}'.format(ANNOTATIONS_KEY_PREFIX, tile.id)

    def _set_default_configuration(self):
        defaults = {}
        tile_type = getUtility(ITileType, name=self.tile.__name__)
        fields = getFieldNamesInOrder(tile_type.schema)

        for name, field in getFieldsInOrder(tile_type.schema):
            order = unicode(fields.index(name))
            # default configuration attributes for all fields
            defaults[name] = {'order': order, 'visibility': u'on'}
            if name == 'css_class':
                # css_class, set default
                defaults[name] = field.default
            if ITextLine.providedBy(field):
                # field is TextLine, we should add 'htmltag'
                defaults[name]['htmltag'] = u'h2'
            elif INamedBlobImageField.providedBy(field):
                # field is an image, we should add 'position' and 'imgsize'
                defaults[name]['position'] = u'left'
                defaults[name]['imgsize'] = u'mini 200:200'

        return defaults

    def get_configuration(self):
        data = dict(self.annotations.get(self.key, {}))

        if not data:
            # tile has no configuration; let's apply the default one
            data = self._set_default_configuration()

        return data

    def set_configuration(self, configuration):
        self.annotations[self.key] = PersistentDict(configuration)

    def delete(self):
        self.annotations.pop(self.key, None)
        return
