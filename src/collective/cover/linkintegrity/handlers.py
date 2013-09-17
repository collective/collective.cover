# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from plone.app.linkintegrity.parser import extractLinks
from plone.app.linkintegrity.references import updateReferences
from plone.app.linkintegrity.handlers import (referencedRelationship, getObjectsFromLinks)
from Products.Archetypes.interfaces import IReferenceable
from plone.app.textfield.value import RichTextValue


def modifiedCoverTile(obj, event):
    """ a dexterity based object was modified """
    pu = getToolByName(obj, 'portal_url', None)
    if pu is None:
        # `getObjectFromLinks` is not possible without access
        # to `portal_url`
        return
    rc = getToolByName(obj, 'reference_catalog', None)
    if rc is None:
        # `updateReferences` is not possible without access
        # to `reference_catalog`
        return
    referenceable_parent = IReferenceable(obj.context, None)
    if referenceable_parent is None:
        # `updateReferences` is not possible
        # if parent object isn't referenceable
        return

    refs = set()

    for name, value in obj.data.items():
        if isinstance(value, RichTextValue):
            value = value.raw
            if not value:
                continue
            links = extractLinks(value)
            refs |= getObjectsFromLinks(obj.context, links)

    updateReferences(IReferenceable(obj.context), referencedRelationship, refs)
