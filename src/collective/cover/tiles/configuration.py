
from persistent.dict import PersistentDict

from zope.annotation.interfaces import IAnnotations

from zope.interface import implements
from zope.interface import Interface


ANNOTATIONS_KEY_PREFIX = u'plone.tiles.configuration'


class ITilesConfigurationScreen(Interface):

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
        self.key = "%s.%s" % (ANNOTATIONS_KEY_PREFIX, tile.id,)

    def get_configuration(self):
        data = dict(self.annotations.get(self.key, {}))

        return data

    def set_configuration(self, configuration):
        self.annotations[self.key] = PersistentDict(configuration)

    def delete(self):
        self.annotations.pop(self.key, None)
        return
