# -*- coding: utf-8 -*-
"""Helper function to test link integrity feature."""
from plone import api


def get_internal_link_html_code():
    """Return HTML code for an internal link to a document."""
    portal = api.portal.get()
    document = portal["my-document"]
    html = '<p><a href="../resolveuid/{0}" data-linktype="internal" data-val="{0}">My Document</a></p>'
    return html.format(document.UID())
