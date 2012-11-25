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
