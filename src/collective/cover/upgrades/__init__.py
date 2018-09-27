# -*- coding: utf-8 -*-
from collective.cover.logger import logger
from plone import api


def cook_css_resources(context):  # pragma: no cover
    """Cook CSS resources."""
    css_tool = api.portal.get_tool('portal_css')
    css_tool.cookResources()
    logger.info('CSS resources were cooked')


def cook_javascript_resources(context):  # pragma: no cover
    """Cook JavaScript resources."""
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.cookResources()
    logger.info('JavaScript resources were cooked')


def get_valid_objects():
    """Generate a list of objects associated with valid brains."""
    results = api.content.find(portal_type='collective.cover.content')
    logger.info('Found {0} objects in the catalog'.format(len(results)))
    for b in results:
        try:
            obj = b.getObject()
        except (AttributeError, KeyError):
            obj = None

        if obj is None:  # warn on broken entries in the catalog
            msg = 'Invalid object reference in the catalog: {0}'
            logger.warn(msg.format(b.getPath()))
            continue

        yield obj
