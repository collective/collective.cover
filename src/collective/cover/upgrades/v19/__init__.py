# -*- coding: utf-8 -*-
from collective.cover.interfaces import ICover
from collective.cover.logger import logger
from plone import api


JS = '++resource++collective.cover/js/layout_edit.js'


def purge_deleted_tiles(context):
    """Purge all annotations of deleted tiles."""
    results = api.content.find(object_provides=ICover.__identifier__)
    logger.info('About to update {0} objects'.format(len(results)))

    for b in results:
        obj = b.getObject()
        obj.purge_deleted_tiles()
        logger.info('Purged annotations on ' + b.getPath())


def register_resource(setup_tool):
    """Add layout_edit.js to registered resources."""
    js_tool = api.portal.get_tool('portal_javascripts')
    js_tool.registerScript(id=JS, compression='none', authenticated=True)
    assert JS in js_tool.getResourceIds()  # nosec
    logger.info('Script registered')
