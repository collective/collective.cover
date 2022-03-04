# -*- coding: utf-8 -*-
from collective.cover.tiles.base import IPersistentCoverTile
from copy import copy
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
                if field_name not in fields:
                    continue  # tile schema has changed

                if not isinstance(field_conf, dict):
                    continue  # field is not ordered

                if field_conf.get("order"):
                    fields[field_name].order = int(field_conf["order"])

    def set(self, data):
        # when setting data, we need to purge scales/image data...
        # XXX hack?
        try:
            scale_key = self.key.replace(".data.", ".scale.")
            del self.storage[scale_key]
        except KeyError:
            pass

        data_copy = copy(data)
        image_modification = False
        for k, v in data_copy.items():
            if INamedImage.providedBy(v):
                mtime_key = "{0}_mtime".format(k)
                if (
                    self.key not in self.storage
                    or k not in self.storage[self.key]
                    or (
                        self.key in self.storage
                        and data[k] != self.storage[self.key][k]
                    )
                ):
                    # set modification time of the image
                    data[mtime_key] = time.time()
                    image_modification = True
                else:
                    data[mtime_key] = self.storage[self.key].get(mtime_key, None)

        self.storage[self.key] = PersistentDict(data)
        if image_modification:
            # Purge tile after put values into storage to prevent old values from
            # being cache, since purge accesses "tile.data".
            notify(Purge(self.tile))
        notify(ObjectModifiedEvent(self.context))
