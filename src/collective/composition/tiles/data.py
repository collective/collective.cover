import time
from datetime import datetime
from persistent.dict import PersistentDict

from zope.component import adapts

from zope.schema import getFields

from plone.tiles.data import PersistentTileDataManager

from collective.composition.tiles.base import IPersistentCompositionTile


class PersistentCompositionTileDataManager(PersistentTileDataManager):
    """
    A data reader for persistent tiles operating on annotatable contexts.
    The data is retrieved from an annotation.
    Specific configuration is applied
    """

    adapts(IPersistentCompositionTile)

    def __init__(self, tile):
        super(PersistentCompositionTileDataManager, self).__init__(tile)
        self.applyTileConfigurations()


    def applyTileConfigurations(self):
        conf = self.tile.get_tile_configuration()
        fields = getFields(self.tileType.schema)

        for field_name, field_conf in conf.items():
            if 'order' in field_conf and field_conf['order']:
                fields[field_name].order = int(field_conf['order'])

    def set(self, data):
        if data.has_key('image'):
            if not self.annotations.has_key(self.key) or \
               (self.annotations.has_key(self.key) and \
                data['image'] != self.annotations[self.key]['image']):
                # set modification time of the image
                data['image_mtime'] = time.mktime(datetime.now().timetuple())
        self.annotations[self.key] = PersistentDict(data)
