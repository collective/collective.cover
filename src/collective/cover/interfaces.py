# -*- coding: utf-8 -*-

from zope.interface import Interface


class ICoverLayer(Interface):
    """ A layer specific for this add-on product.
    """


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
