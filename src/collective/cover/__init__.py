# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import setDefaultRoles
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.cover')

setDefaultRoles(
    'collective.cover: Can Export Layout', ('Manager', 'Site Administrator'))
