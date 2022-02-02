# -*- coding: utf-8 -*-
from collective.cover.logger import logger
from plone import api


def get_valid_objects():
    """Generate a list of objects associated with valid brains."""
    results = api.content.find(portal_type="collective.cover.content")
    logger.info("Found {0} objects in the catalog".format(len(results)))
    for b in results:
        try:
            obj = b.getObject()
        except (AttributeError, KeyError):
            obj = None

        if obj is None:  # warn on broken entries in the catalog
            msg = "Invalid object reference in the catalog: {0}"
            logger.warn(msg.format(b.getPath()))
            continue

        yield obj
