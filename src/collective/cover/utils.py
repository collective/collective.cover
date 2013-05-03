# -*- coding: utf-8 -*-

import uuid


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
