# -*- coding: utf-8 -*-
from Products.CMFPlone import interfaces as Plone
from Products.CMFQuickInstallerTool import interfaces as QuickInstaller
from zope.interface import implements


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
