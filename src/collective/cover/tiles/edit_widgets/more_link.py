# -*- coding: utf-8 -*-

from interfaces import IMoreLinkWidget
from Products.CMFCore.utils import getToolByName
from z3c.form import interfaces
from z3c.form.browser.text import TextWidget
from z3c.form.widget import FieldWidget

import zope.interface
import zope.schema


@zope.interface.implementer_only(IMoreLinkWidget)
class MoreLinkWidget(TextWidget):
    """Select widget implementation."""

    def link_title(self):
        if not self.value:
            return None

        pc = getToolByName(self.form.context, 'portal_catalog')
        brainz = pc(UID=self.value)
        if len(brainz):
            return brainz[0].Title

        return None


@zope.component.adapter(zope.schema.interfaces.ITextLine,
                        zope.interface.Interface,
                        interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def MoreLinkFieldWidget(field, source, request=None):
    """IFieldWidget factory for MoreLinkWidget."""
    # BBB: emulate our pre-2.0 signature (field, request)
    if request is None:
        real_request = source
    else:
        real_request = request

    return FieldWidget(field, MoreLinkWidget(real_request))
