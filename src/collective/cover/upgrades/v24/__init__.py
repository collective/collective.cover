# -*- coding: utf-8 -*-
from collective.cover.logger import logger
from plone import api


SCRIPTS = [
    '++resource++collective.cover/js/contentchooser.js',
    '++resource++collective.cover/js/vendor/jquery.endless-scroll.js',
    '++resource++collective.cover/js/layout_edit.js',
    '++resource++collective.cover/js/main.js',
]
STYLES = [
    '++resource++collective.cover/css/contentchooser.css',
    '++resource++collective.cover/css/cover.css',
]


def deprecate_resource_registries(setup_tool):
    """Deprecate resource registries."""
    js_tool = api.portal.get_tool('portal_javascripts')
    for js in SCRIPTS:
        js_tool.unregisterResource(id=js)
        assert js not in js_tool.getResourceIds()  # nosec
    logger.info('Scripts removed')

    css_tool = api.portal.get_tool('portal_css')
    for css in STYLES:
        css_tool.unregisterResource(id=css)
        assert css not in css_tool.getResourceIds()  # nosec
    logger.info('Styles removed')
