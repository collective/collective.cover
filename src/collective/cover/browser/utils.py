# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.cover.browser.interfaces import IHelper
from collective.cover.interfaces import ICover
from Products.Five.browser import BrowserView
from zope.interface import implements


class Helper(BrowserView):

    """Helper view used to determine if resources are being loaded or not."""

    implements(IHelper)

    def __call__(self):
        self.context = aq_inner(self.context)
        self.is_cover = ICover.providedBy(self.context)
        # the name of the template is in the parent request
        if self.is_cover and 'PARENT_REQUEST' in self.request:
            # template name is the last part of the URL
            url = self.request.PARENT_REQUEST.URL
            self.mode = url.split('/')[-1]
        else:
            self.mode = ''

    def is_view_mode(self):
        """True if we are in the context of a cover object in view mode."""
        return self.mode == 'view'

    def is_compose_mode(self):
        """True if we are in the context of a cover object in compose mode."""
        return self.mode == 'compose'

    def is_layout_mode(self):
        """True if we are in the context of a cover object in layout mode."""
        return self.mode == 'layout'
