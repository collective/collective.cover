from zope.interface import Interface


class IHelper(Interface):

    """Helper view used to determine if resources are being loaded or not."""

    def is_view_mode():
        """True if we are in the context of a cover object in view mode."""

    def is_compose_mode():
        """True if we are in the context of a cover object in compose mode."""

    def is_layout_mode():
        """True if we are in the context of a cover object in layout mode."""
