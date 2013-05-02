# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
from Products.CMFCore.permissions import setDefaultRoles

_ = MessageFactory('collective.cover')

setDefaultRoles(
    'collective.cover: Can Export Layout', ('Manager', 'Site Administrator'))
