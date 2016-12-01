# -*- coding: utf-8 -*-
"""Helper function to test link integrity feature."""
from collective.cover.config import IS_PLONE_5
from plone import api
from plone.app.referenceablebehavior.referenceable import IReferenceable
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility

import transaction


NEEDS_REFERENCEABLE_BEHAVIOR = not IS_PLONE_5


def setup_link_integrity():
    if NEEDS_REFERENCEABLE_BEHAVIOR:
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        behaviors = list(fti.behaviors)
        behaviors.append(IReferenceable.__identifier__)
        fti.behaviors = tuple(behaviors)
        transaction.commit()


def teardown_link_integrity():
    if NEEDS_REFERENCEABLE_BEHAVIOR:
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        behaviors = list(fti.behaviors)
        behaviors.remove(IReferenceable.__identifier__)
        fti.behaviors = tuple(behaviors)
        transaction.commit()


def get_internal_link_html_code():
    """Return HTML code for an internal link to a document."""
    portal = api.portal.get()
    document = portal['my-document']
    html = '<p><a class="internal-link" href="resolveuid/{0}">My Document</a></p>'
    return html.format(document.UID())
