# -*- coding: utf-8 -*-
from plone.directives import form
from zope.interface import Attribute
from zope.interface import Interface


class ICoverLayer(Interface):
    """ A layer specific for this add-on product.
    """


class ICover(form.Schema):

    """A composable page."""

    form.model('models/cover.xml')


class IJSONSearch(Interface):
    """ Returns a list of search results in JSON """

    def __init__(self, context):
        """  Constructor """

    def getBreadcrumbs(self):
        """Get breadcrumbs"""

    def getSearchResults(self, filter_portal_types, rooted, document_base_url, searchtext):
        """ Returns the actual search results """


class ICoverUIDsProvider(Interface):

    def getUIDs(self):
        """ Get UIDs associated with the object.
            could be the UID of the object or a
            list of related UIDs.

        @return: iterable of UIDs
        """


class ITileEditForm(Interface):
    """Custom EditForm interface for a tile.
    """


class IGridSystem(Interface):
    """Interface for classes that implement a grid system for collective
    cover."""

    title = Attribute('The user-visible title for this grid.')
    ncolums = Attribute('Number of colums in a grid.')
