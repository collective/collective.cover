
from AccessControl import Unauthorized

from zope.publisher.interfaces.browser import IBrowserView

from plone.app.tiles.browser.edit import DefaultEditForm
from plone.app.tiles.browser.edit import DefaultEditView

from plone.app.tiles.browser.traversal import EditTile


class ICompositionTileEditView(IBrowserView):
    """
    """

class CustomEditForm(DefaultEditForm):
    """Standard tile edit form, which is wrapped by DefaultEditView (see
    below).

    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """

    def update(self):
        super(CustomEditForm, self).update()

        typeName = self.tileType.__name__
        tileId = self.tileId

        tile = self.context.restrictedTraverse('@@%s/%s' % (typeName, tileId,))

        if not tile.isAllowedToEdit():
            raise Unauthorized("You are not allowed to add this kind of tile")


class CustomTileEdit(DefaultEditView):
    """
    Override the default @@edit-tile so we can raise Unauthorized using our
    custom security implementation
    """

    form = CustomEditForm


class CompositionTileEditView(EditTile):
    """
    Implements the @@edit-tile namespace for our specific tiles, so we can
    check permissions.
    """

    targetInterface = ICompositionTileEditView
