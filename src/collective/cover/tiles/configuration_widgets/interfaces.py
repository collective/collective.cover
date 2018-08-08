# -*- coding: utf-8 -*-
from plone.formwidget.namedfile.interfaces import INamedImageWidget as INamedImageWidgetBase
from z3c.form import interfaces


class ICSSClassWidget(interfaces.ISelectWidget):
    """CSSClass Select widget."""


class INamedImageWidget(INamedImageWidgetBase):
    """A widget for a named image field."""
