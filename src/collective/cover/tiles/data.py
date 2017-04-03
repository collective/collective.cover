# -*- coding: utf-8 -*-
from collective.cover.tiles.base import IPersistentCoverTile
from persistent.dict import PersistentDict
from plone.namedfile.interfaces import INamedImage
from plone.tiles.data import PersistentTileDataManager
from z3c.caching.purge import Purge
from zope.component import adapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFields

import time


@adapter(IPersistentCoverTile)
class PersistentCoverTileDataManager(PersistentTileDataManager):
    """
    A data reader for persistent tiles operating on annotatable contexts.
    The data is retrieved from an annotation.
    Specific configuration is applied
    """

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
        # when setting data, we need to purge scales/image data...
        # XXX hack?
        try:
            scale_key = self.key.replace('.data.', '.scale.')
            del self.annotations[scale_key]
        except KeyError:
            pass

        for k, v in data.items():
            if INamedImage.providedBy(v):
                mtime_key = '{0}_mtime'.format(k)
                if (self.key not in self.annotations or
                    k not in self.annotations[self.key] or
                    (self.key in self.annotations and
                     data[k] != self.annotations[self.key][k])):
                    # set modification time of the image
                    notify(Purge(self.tile))
                    data[mtime_key] = time.time()
                else:
                    data[mtime_key] = self.annotations[self.key].get(mtime_key, None)

        self.annotations[self.key] = PersistentDict(data)
        notify(ObjectModifiedEvent(self.context))
