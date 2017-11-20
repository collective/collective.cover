# -*- coding: utf-8 -*-
from collective.cover.interfaces import ICover
from collective.cover.logger import logger
from plone import api


TO_REGISTER = '++resource++collective.cover/js/layout_edit.js'


def purge_deleted_tiles(context):
    """Purge all annotations of deleted tiles."""

    covers = context.portal_catalog(object_provides=ICover.__identifier__)
    logger.info('About to update {0} objects'.format(len(covers)))
    for cover in covers:
        obj = cover.getObject()
        obj.purge_deleted_tiles()
        msg = 'Cover {0} updated'
        logger.info(msg.format(cover.getPath()))

    logger.info('Done')


def register_resource(setup_tool):
    """Add layout_edit.js to registered resources."""
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.registerResource(id=TO_REGISTER, authenticated=True)
    logger.info('Resource registered.')
