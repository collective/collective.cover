# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import pkg_resources


try:
    pkg_resources.get_distribution('plone.app.relationfield')
except pkg_resources.DistributionNotFound:
    HAS_RELATIONFIELD = False
else:
    HAS_RELATIONFIELD = True


@implementer(INonInstallable)
class HiddenProfiles(object):  # pragma: no cover

    def getNonInstallableProfiles(self):
        """Do not show on Plone's list of installable profiles."""
        return [
            u'collective.cover:testfixture',
            u'collective.cover:uninstall',
        ]


def add_default_layout():
    """Add an empty layout as default."""
    from collective.cover.config import EMPTY_LAYOUT
    from collective.cover.controlpanel import ICoverSettings
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICoverSettings)
    default = u'Empty layout'
    if settings.layouts.get(default) == u'[]':
        settings.layouts[default] = EMPTY_LAYOUT


def install_relationfield():
    """Install plone.app.relationfield."""
    from plone import api
    qi = api.portal.get_tool('portal_quickinstaller')
    qi.installProduct('plone.app.relationfield')
    fti = api.portal.get_tool('portal_types')['collective.cover.content']
    fti.behaviors += ('plone.app.relationfield.behavior.IRelatedItems',)


def run_after(portal_setup):
    add_default_layout()

    if HAS_RELATIONFIELD:
        install_relationfield()
