# -*- coding: utf-8 -*-

import uuid
from plone import api

def assign_tile_ids(layout, override=True):
    """
    This function takes a dict, and it will recursively traverse it and assign
    sha-hashed ids so we are pretty sure they are unique among them
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
    """Given a UUID, attempt to return a content object. Will return
    None if the UUID can't be found. 
    """
    
    # Use local uuidToCatalogBrain without the inactive content filter 
    brain = uuidToCatalogBrain(uuid)
    if brain is None:
        return None
    
    return brain.getObject()

def uuidToCatalogBrain(uuid):
    """Given a UUID, attempt to return a catalog brain.
       Copied from plone.app.uuid:utils but doesn't filter on expired items
    """
    
    catalog = api.portal.get_tool(name='portal_catalog')
    if catalog is None:
        return None
    
    result = catalog(UID=uuid, show_all=1, show_inactive=1)
    if len(result) != 1:
        return None
    
    return result[0]