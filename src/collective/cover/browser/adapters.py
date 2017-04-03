# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFPlone.browser.ploneview import Plone


class PloneView(Plone):

    def renderBase(self):
        """We need to return the cover url with a slash at the end
        so relative calls to javascript are called for the cover object
        and not its parent
        """
        context = aq_inner(self.context)
        return context.absolute_url() + '/'
