# -*- coding: utf-8 -*-

from collective.cover.content import ICover
from five import grok
from plone.app.iterate.interfaces import ICheckinEvent
from plone.app.linkintegrity.handlers import getObjectsFromLinks
from plone.app.linkintegrity.handlers import referencedRelationship
from plone.app.linkintegrity.parser import extractLinks
from plone.app.linkintegrity.references import updateReferences
from plone.app.textfield.value import RichTextValue
from Products.Archetypes.interfaces import IReferenceable
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations


@grok.subscribe(ICover, ICheckinEvent)
def override_object_annotations(cover, event):
    """
    We need to override the annotations stored in the old object with the
    ones in the working copy, and to do that, we first need to remove
    old entries.
    """

    old_annotations = IAnnotations(event.baseline)
    new_annotations = IAnnotations(event.object)

    for key in old_annotations:
        # First remove all annotations in relation to tiles
        if key.startswith('plone.tiles.'):
            del old_annotations[key]

    for key in new_annotations:
        # Now, copy the ones from the new annotations
        if key.startswith('plone.tiles.'):
            old_annotations[key] = new_annotations[key]


def modifiedCoverTile(obj, event):
    """Ensure link integrity on Rich Text tiles.

    Keyword arguments:
    obj -- Dexterity-based object that was modified
    event -- event fired
    """
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
