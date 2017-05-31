# -*- coding: utf-8 -*-
from plone.supermodel import model
from zope.interface import Attribute
from zope.interface import Interface

import warnings


class ICoverLayer(Interface):
    """ A layer specific for this add-on product.
    """


class ICover(model.Schema):

    """A composable page."""

    model.load('models/cover.xml')


class IJSONSearch(Interface):
    """ Returns a list of search results in JSON """

    def __init__(self, context):
        """  Constructor """

    def getBreadcrumbs(self):
        """Get breadcrumbs"""

    def getSearchResults(self, filter_portal_types, rooted, document_base_url, searchtext):
        """ Returns the actual search results """


class ICoverUIDsProvider(Interface):
    """GenericUIDsProvider interface will be removed in collective.cover v1.7."""
    warnings.warn(__doc__, DeprecationWarning)


class ITileEditForm(Interface):
    """Custom EditForm interface for a tile.
    """


class IGridSystem(Interface):
    """Interface for classes that implement a grid system for collective
    cover."""

    title = Attribute('The user-visible title for this grid.')
    ncolums = Attribute('Number of colums in a grid.')


class ISearchableText(Interface):

    """Interface to adapt tile to provide indexable content."""

    def SearchableText(self):
        """Content of the tile provided as plain text."""
