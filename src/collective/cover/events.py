# -*- coding: utf-8 -*-
from collective.cover.config import PLONE_VERSION
from collective.cover.interfaces import ICover
from five import grok
from plone.app.iterate.interfaces import ICheckinEvent
from plone.app.linkintegrity.handlers import getObjectsFromLinks
from plone.app.linkintegrity.parser import extractLinks
from plone.app.textfield.value import RichTextValue
from zope.annotation.interfaces import IAnnotations

if PLONE_VERSION.startswith('5'):
    from plone.app.linkintegrity.handlers import updateReferences
else:
    from plone.app.linkintegrity.handlers import referencedRelationship
    from plone.app.linkintegrity.references import updateReferences
    from Products.Archetypes.interfaces import IReferenceable


@grok.subscribe(ICover, ICheckinEvent)
def override_object_annotations(cover, event):
    """
    We need to override the annotations stored in the old object with the
    ones in the working copy, and to do that, we first need to remove
    old entries.
    """

    old_annotations = IAnnotations(event.baseline)
    new_annotations = IAnnotations(event.object)

    old_keys = list(old_annotations.keys())
    for key in old_keys:
        # First remove all annotations in relation to tiles
        if key.startswith('plone.tiles.'):
            del old_annotations[key]

    for key in new_annotations:
        # Now, copy the ones from the new annotations
        if key.startswith('plone.tiles.'):
            old_annotations[key] = new_annotations[key]


def update_link_integrity(obj, event):
    """Update link integrity information on modification/removal of
    tiles.

    :param obj: cover object that was modified
    :type obj: Dexterity-based content type
    :param event: event fired
    :type event:
    """
    refs = set()
    for name, value in obj.data.items():
        if isinstance(value, RichTextValue):
            value = value.raw
            if not value:
                continue
            links = extractLinks(value)
            refs |= getObjectsFromLinks(obj.context, links)

    if PLONE_VERSION.startswith('5'):
        updateReferences(obj.context, refs)
    elif IReferenceable.providedBy(obj.context):
        updateReferences(IReferenceable(obj.context), referencedRelationship, refs)
