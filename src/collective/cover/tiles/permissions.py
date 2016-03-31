# -*- coding: utf-8 -*-

from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.interface import Interface


ANNOTATIONS_KEY_PREFIX = u'plone.tiles.permission'


class ITilesPermissions(Interface):

    def get_allowed_edit():
        """
        Get the list of groups that are allowed to add content to the tile
        """

    def set_allowed_edit(group_ids):
        """
        Set the list of groups that are allowed to add content to the tile
        """

    def delete():
        """
        Remove the list of groups that are allowed to add content to the tile
        """


@implementer(ITilesPermissions)
class TilesPermissions(object):
    """
    An adapter that will provide store permissions for a tile
    """

    def __init__(self, context, request, tile):
        self.context = context
        self.request = request
        self.tile = tile
        self.annotations = IAnnotations(self.context)
        self.key = '{0}.{1}'.format(ANNOTATIONS_KEY_PREFIX, tile.id)

    def get_allowed_edit(self):
        permissions = dict(self.annotations.get(self.key, {}))

        return permissions.get('edit', ())

    def set_allowed_edit(self, group_ids):
        permissions = dict(self.annotations.get(self.key, {}))

        if isinstance(group_ids, list):
            group_ids = tuple(group_ids)
        elif isinstance(group_ids, basestring):
            group_ids = (group_ids,)

        permissions['edit'] = group_ids

        self.annotations[self.key] = PersistentDict(permissions)

    def delete(self):
        self.annotations.pop(self.key, None)
        return
