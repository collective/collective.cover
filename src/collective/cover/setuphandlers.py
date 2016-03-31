# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implements


class HiddenProfiles(object):

    implements(Plone.INonInstallable)

    def getNonInstallableProfiles(self):
        """Do not show on Plone's list of installable profiles."""
        return [
            u'collective.cover:testfixture',
            u'collective.cover:uninstall',
        ]
