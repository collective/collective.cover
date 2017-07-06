# -*- coding: utf-8 -*-

from collective.cover.tiles.richtext import IRichTextTile
from plone.app.widgets.dx import RichTextWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer


@adapter(getSpecification(IRichTextTile['text']), IFormLayer)
@implementer(IFieldWidget)
def TileRichTextFieldWidget(field, request):
    return FieldWidget(field, RichTextWidget(request))
