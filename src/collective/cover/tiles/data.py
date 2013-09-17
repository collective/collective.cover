# -*- coding: utf-8 -*-

from collective.cover.tiles.base import IPersistentCoverTile
from persistent.dict import PersistentDict
from plone.namedfile.interfaces import INamedImage
from plone.tiles.data import PersistentTileDataManager
from z3c.caching.purge import Purge
from zope.component import adapts
from zope.event import notify
from zope.schema import getFields
from zope.lifecycleevent import ObjectModifiedEvent

import time


class PersistentCoverTileDataManager(PersistentTileDataManager):
    """
    A data reader for persistent tiles operating on annotatable contexts.
    The data is retrieved from an annotation.
    Specific configuration is applied
    """

    adapts(IPersistentCoverTile)

    def __init__(self, tile):
        super(PersistentCoverTileDataManager, self).__init__(tile)
        self.applyTileConfigurations()

    def applyTileConfigurations(self):
        conf = self.tile.get_tile_configuration()
        if self.tileType:
            fields = getFields(self.tileType.schema)

            for field_name, field_conf in conf.items():
                if 'order' in field_conf and field_conf['order']:
                    fields[field_name].order = int(field_conf['order'])

    def set(self, data):
        for k, v in data.items():
            if INamedImage.providedBy(v):
                if (self.key not in self.annotations or
                    k not in self.annotations[self.key] or
                    (self.key in self.annotations and
                     data[k] != self.annotations[self.key][k])):
                    # set modification time of the image
                    notify(Purge(self.tile))
                    data['{0}_mtime'.format(k)] = '%f' % time.time()
        self.annotations[self.key] = PersistentDict(data)
        notify(ObjectModifiedEvent(self.context))
