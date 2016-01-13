# -*- coding: utf-8 -*-
from collective.cover.config import PROJECTNAME
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone import interfaces as Plone
from Products.CMFQuickInstallerTool import interfaces as QuickInstaller
from zope.component import queryUtility
from zope.interface import implements

import logging
import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.stagingbehavior')
except pkg_resources.DistributionNotFound:
    IStagingSupport = None
else:
    from plone.app.stagingbehavior.interfaces import IStagingSupport


class HiddenProfiles(object):

    implements(Plone.INonInstallable)

    def getNonInstallableProfiles(self):
        """Do not show on Plone's list of installable profiles."""
        return [
            u'collective.cover:testfixture',
            u'collective.cover:uninstall',
        ]


class HiddenProducts(object):

    implements(QuickInstaller.INonInstallable)

    def getNonInstallableProducts(self):
        """Do not show on QuickInstaller's list of installable products."""
        return [
        ]


def import_various(context):
    """Import step for configuration that is not handled in XML files:

    Add staging behavior to content type. This will not be needed
    under Plone 5 as checkout and checkin operations are directly
    provided by plone.app.iterate.
    """
    if context.readDataFile('collective.cover.marker.txt') is None:
        return

    if IStagingSupport is not None:
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        behaviors = list(fti.behaviors)

        if IStagingSupport.__identifier__ in behaviors:
            return

        behaviors.append(IStagingSupport.__identifier__)
        fti.behaviors = tuple(behaviors)
        logger = logging.getLogger(PROJECTNAME)
        logger.info('Staging behavior for Cover content type was enabled.')
