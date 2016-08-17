# -*- coding: utf-8 -*-
from collective.cover.config import PROJECTNAME
from collective.cover.interfaces import ICover
from collective.cover.logger import logger
from collective.cover.subscribers import update_link_integrity
from plone import api


RESOURCES_TO_FIX = {
    '++resource++collective.cover/contentchooser.css': '++resource++collective.cover/css/contentchooser.css',
    '++resource++collective.cover/cover.css': '++resource++collective.cover/css/cover.css',
    '++resource++collective.cover/contentchooser.js': '++resource++collective.cover/js/contentchooser.js',
    '++resource++collective.cover/jquery.endless-scroll.js': '++resource++collective.cover/js/vendor/jquery.endless-scroll.js'
}


def _rename_resources(tool, from_to):
    for id in tool.getResourceIds():
        if id in from_to:
            tool.renameResource(id, from_to[id])


def fix_resources_references(setup_tool):
    """Fix resource references after static files reorganization."""
    profile = 'profile-{0}:default'.format(PROJECTNAME)

    css_tool = api.portal.get_tool('portal_css')
    _rename_resources(css_tool, RESOURCES_TO_FIX)
    logger.info('Updated css references.')

    js_tool = api.portal.get_tool('portal_javascripts')
    _rename_resources(js_tool, RESOURCES_TO_FIX)
    logger.info('Updated javascript references.')

    setup_tool.runImportStepFromProfile(profile, 'controlpanel')
    logger.info('Updated controlpanel icon reference.')

    setup_tool.runImportStepFromProfile(profile, 'typeinfo')
    logger.info('Updated content type icon reference.')


def update_references(setup_tool):
    """Update references used for link integrity checking."""
    catalog = api.portal.get_tool('portal_catalog')
    query = dict(object_provides=ICover.__identifier__)
    results = catalog.unrestrictedSearchResults(**query)
    for brain in results:
        obj = brain.getObject()
        try:
            update_link_integrity(obj, None)
        except AssertionError:
            msg = 'Duplicated tiles in {0} ({1}); skipping'
            logger.error(msg.format(obj.absolute_url(), obj.list_tiles()))

    logger.info('References updated on {0} objects.'.format(len(results)))
