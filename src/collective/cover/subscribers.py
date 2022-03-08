# -*- coding: utf-8 -*-
from collective.cover.controlpanel import ICoverSettings
from collective.cover.utils import assign_tile_ids
from plone.app.linkintegrity.handlers import updateReferences
from plone.registry.interfaces import IRegistry
from z3c.relationfield.relation import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import json


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
        if key.startswith("plone.tiles."):
            del old_annotations[key]

    for key in new_annotations:
        # Now, copy the ones from the new annotations
        if key.startswith("plone.tiles."):
            old_annotations[key] = new_annotations[key]


def update_link_integrity(obj, event):
    """Update link integrity information on modification/removal of
    tiles.

    :param obj: cover object that was modified
    :type obj: Dexterity-based content type
    :param event: event fired
    :type event:
    """
    refs = obj.get_referenced_objects()

    intids = getUtility(IIntIds)
    getId = intids.getId
    new_relationships = []
    for ref in refs:
        if ref:
            # When content is referenced as an internal link in a rich text tile,the
            # 'ref' is a RelationValue. So we don't need to create a new RelationValue.
            if isinstance(ref, RelationValue):
                new_relationships.append(ref)
            else:
                new_relationships.append(RelationValue(getId(ref)))

    updateReferences(obj, new_relationships)


def assign_id_for_tiles(cover, event):
    if not cover.cover_layout:
        # When versioning, a new cover gets created, so, if we already
        # have a cover_layout stored, do not overwrite it
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)

        layout = settings.layouts.get(cover.template_layout)
        if layout:
            layout = json.loads(layout)
            assign_tile_ids(layout)

            cover.cover_layout = json.dumps(layout)
