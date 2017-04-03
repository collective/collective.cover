# -*- coding: utf-8 -*-
from collective.cover.config import IS_PLONE_5
from plone import api

import uuid


def assign_tile_ids(layout, override=True):
    """Recursively traverse a dict describing a layout and assign
    sha-hashed ids to the tiles so we are pretty sure they are unique
    among them.
    """

    for elem in layout:
        if elem.get('type') == u'tile':
            if 'id' not in elem or not elem['id'] or override:
                elem['id'] = uuid.uuid4().hex
        else:
            children = elem.get('children')
            if children:
                assign_tile_ids(children, override)


def uuidToObject(uuid):
    """Return a content object given an UUID.

    :param uuid: UUID of the object
    :type uuid: str
    :returns: the content object or None, if the UUID can't be found.
    """
    # Use local uuidToCatalogBrain without the inactive content filter
    brain = uuidToCatalogBrain(uuid)
    return brain.getObject() if brain else None


# TODO: implement this directly in plone.app.uuid
def uuidToCatalogBrain(uuid):
    """Return a catalog brain given an UUID.
    Copied from plone.app.uuid:utils but doesn't filter on expired items.

    :param uuid: UUID of the object
    :type uuid: str
    :returns: the catalog brain associated with the object or None,
        if the UUID can't be found.
    """
    catalog = api.portal.get_tool('portal_catalog')
    # XXX: should we add a check on 'Access inactive portal content'
    #      permission before setting show_inactive?
    results = catalog(UID=uuid, show_all=1, show_inactive=1)
    return results[0] if results else None


def get_types_use_view_action_in_listings():
    """Helper funtion to deal with API inconsistencies."""
    if IS_PLONE_5:
        return api.portal.get_registry_record('plone.types_use_view_action_in_listings')
    else:
        portal_properties = api.portal.get_tool(name='portal_properties')
        site_properties = portal_properties.site_properties
        return site_properties.getProperty('typesUseViewActionInListings', ())
