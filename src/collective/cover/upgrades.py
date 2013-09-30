# -*- coding: utf-8 -*-

from collective.cover.config import PROJECTNAME
from collective.cover.content import ICover
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

import logging


def rename_content_chooser_resources(context, logger=None):
    """Handler for upgrade step from 2 to 3; renames the 'screenlets'
    resources to 'contentchooser'.
    See: https://github.com/collective/collective.cover/issues/165
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    # first we take care of the CSS registry
    css_tool = getToolByName(context, 'portal_css')
    old_id = '++resource++collective.cover/screenlets.css'
    new_id = '++resource++collective.cover/contentchooser.css'
    if old_id in css_tool.getResourceIds():
        css_tool.renameResource(old_id, new_id)
        logger.info("'{0}' resource was renamed to '{1}'".format(old_id, new_id))
        css_tool.cookResources()
        logger.info("CSS resources were cooked")
    else:
        logger.debug("'{0}' resource not found in portal_css".format(old_id))

    # now we mess with the JS registry
    js_tool = getToolByName(context, 'portal_javascripts')
    old_id = '++resource++collective.cover/screenlets.js'
    new_id = '++resource++collective.cover/contentchooser.js'
    if old_id in js_tool.getResourceIds():
        js_tool.renameResource(old_id, new_id)
        logger.info("'{0}' resource was renamed to '{1}'".format(old_id, new_id))
        js_tool.cookResources()
        logger.info("JS resources were cooked")
    else:
        logger.debug("'{0}' resource not found in portal_javascripts".format(old_id))


def register_available_tiles_record(context, logger=None):
    """Handler for upgrade step from 2 to 3; adds the 'available_tiles' record
    to the registry.
    See: https://github.com/collective/collective.cover/issues/191
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    registry = getUtility(IRegistry)
    record = 'collective.cover.controlpanel.ICoverSettings.available_tiles'

    if record not in registry.records:
        profile = 'profile-collective.cover:upgrade_2_to_3'
        setup = getToolByName(context, 'portal_setup')
        setup.runAllImportStepsFromProfile(profile)
        logger.info("'available_tiles' record added to the registry")
    else:
        logger.debug("'available_tiles' record already in the registry")


def register_styles_record(context, logger=None):
    """Handler for upgrade step from 3 to 4; adds the 'styles' record
    to the registry.
    See: https://github.com/collective/collective.cover/issues/190
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    registry = getUtility(IRegistry)
    record = 'collective.cover.controlpanel.ICoverSettings.styles'

    if record in registry.records:
        # XXX: if the record is on the registry it will be corrupt by a type
        # mismatch and we need just to remove it; this could happen only in
        # case of sites using collective.cover from master branch
        del registry.records[record]

    profile = 'profile-collective.cover:upgrade_3_to_4'
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile(profile)
    logger.info("'styles' record added to the registry")


def issue_218(context, logger=None):
    """Unregister image and link tiles from plone.app.tiles to avoid further
    addition of them in covers; register new banner tile.
    See: https://github.com/collective/collective.cover/issues/218
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    def upgrade_record():
        tile = u'collective.cover.banner'
        if tile not in record:
            record.append(tile)
            logger.info(
                "'{0}' tile added to '{1}' record".format(tile, record_name))
        else:
            logger.debug(
                "'{0}' tile already in '{1}' record".format(tile, record_name))

        for tile in (u'collective.cover.image', u'collective.cover.link'):
            if tile in record:
                record.remove(tile)
                logger.info(
                    "'{0}' tile removed from '{1}' record".format(tile, record_name))
            else:
                logger.debug(
                    "'{0}' tile already removed from '{1}' record".format(tile, record_name))

        record.sort()
        registry[record_name] = record

    registry = getUtility(IRegistry)
    record_name = u'plone.app.tiles'
    record = registry[record_name]
    upgrade_record()

    record_name = u'collective.cover.controlpanel.ICoverSettings.available_tiles'
    record = registry[record_name]
    if u'collective.cover.image' in record or \
       u'collective.cover.link' in record:
        upgrade_record()


def issue_244(context, logger=None):
    """Add cover.css to css_registry.
    See: https://github.com/collective/collective.cover/issues/244
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    css_tool = getToolByName(context, 'portal_css')
    id = '++resource++collective.cover/cover.css'
    if id not in css_tool.getResourceIds():
        css_tool.registerStylesheet(id)
        logger.info("{0} resource was added".format(id))
        css_tool.cookResources()
        logger.info("CSS resources were cooked")
    else:
        logger.debug("{0} resource already in portal_css".format(id))


def issue_262(context, logger=None):
    """Default value for css_class.
    See: https://github.com/collective/collective.cover/issues/262
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    profile = 'profile-collective.cover:upgrade_4_to_5'
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(profile, 'plone.app.registry')
    logger.info("'styles' record updated in the registry")

    new_default_value = u"tile-default"
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(object_provides=ICover.__identifier__)

    # update existing tiles with default value
    for brain in brains:
        cover = brain.getObject()
        layout_view = cover.restrictedTraverse("layout")

        # There might be covers with empty layout
        try:
            layout = layout_view.get_layout("view")
        except:
            layout = []
        for row in layout:
            for column in row.get("children", []):
                for tile_data in column.get("children", []):
                    tile = cover.restrictedTraverse("{0}/{1}".format(
                        tile_data["tile-type"], tile_data["id"]))
                    tile_config = tile.get_tile_configuration()
                    css_class = tile_config.get("css_class", u"")
                    if not isinstance(css_class, basestring) or css_class == u"--NOVALUE--" or css_class == u"":
                        tile_config['css_class'] = new_default_value
                        tile.set_tile_configuration(tile_config)

    logger.info("Default value was set on all 'css_class' fields")


def issue_259(context, logger=None):
    """Make cover linkable from TinyMCE.
    See: https://github.com/collective/collective.cover/issues/259
    """

    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    profile = 'profile-collective.cover:upgrade_4_to_5'
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(profile, 'tinymce_settings')
    logger.info("'linkable' property updated in TinyMCE settings")


def issue_271(context, logger=None):
    """Implement standard content type view.
    See: https://github.com/collective/collective.cover/issues/271
    """

    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    profile = 'profile-collective.cover:upgrade_4_to_5'
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(profile, 'typeinfo')
    logger.info("Alternate view for collective.cover.content objects added.")


def issue_35(context, logger=None):
    """Link integrity on Rich Text tile references.
    See: https://github.com/collective/collective.cover/issues/35
    """

    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    fti = getUtility(IDexterityFTI, name='collective.cover.content')
    referenceable = u'plone.app.referenceablebehavior.referenceable.IReferenceable'
    behaviors = list(fti.behaviors)
    if referenceable not in behaviors:
        behaviors.append(referenceable)
        fti.behaviors = tuple(behaviors)
        logger.info("collective.cover objects are now referenceable.")


def issue_294(context, logger=None):
    """Install IRelatedItems behavior.
    See: https://github.com/collective/collective.cover/issues/294
    """
    if logger is None:
        logger = logging.getLogger(PROJECTNAME)

    fti = getUtility(IDexterityFTI, name='collective.cover.content')
    related_items = u'plone.app.relationfield.behavior.IRelatedItems'
    behaviors = list(fti.behaviors)
    if related_items not in behaviors:
        behaviors.append(related_items)
        fti.behaviors = tuple(behaviors)
        logger.info("IRelatedItems behavior was installed.")
