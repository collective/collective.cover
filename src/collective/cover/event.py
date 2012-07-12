from five import grok

from zope.annotation.interfaces import IAnnotations

from plone.app.iterate.interfaces import ICheckinEvent

from collective.cover.content import ICover


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
