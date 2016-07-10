# -*- coding: utf-8 -*-
from plone.app.layout.globals import layout as base
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility


class LayoutPolicy(base.LayoutPolicy):

    """Override the default Plone layout utility."""

    def bodyClass(self, template, view):
        """Include layout identifier in bodyClass."""
        body_class = super(LayoutPolicy, self).bodyClass(template, view)
        util = getUtility(IIDNormalizer)
        layout_id = util.normalize(self.context.template_layout)
        return 'cover-layout-{0} {1}'.format(layout_id, body_class)
