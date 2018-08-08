# -*- coding: utf-8 -*-
from interfaces import INamedImageWidget
from plone.formwidget.namedfile.widget import NamedImageWidget as NamedImageWidgetBase
from plone.namedfile.interfaces import INamedImageField
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IVocabularyFactory


@implementer_only(INamedImageWidget)
class NamedImageWidget(NamedImageWidgetBase):
    """A widget for a named file object."""

    def allowed_sizes(self):
        stored_data = self.form.getFieldConfiguration(self)
        selected = stored_data.get('imgsize', None)

        factory = getUtility(
            IVocabularyFactory, 'plone.app.vocabularies.ImagesScales')
        vocabulary = factory(self.context)
        items = [
            {
                'title': term.title,
                'value': term.title,
                'selected': 'selected' if selected == term.value else None,
            }
            for term in vocabulary
        ]
        items.append({
            'title': 'Original Size',
            'value': '_original',
            'selected': 'selected' if selected == '_original' else None,
        })
        return items


@implementer(IFieldWidget)
@adapter(INamedImageField, IFormLayer)
def NamedImageFieldWidget(field, request):
    return FieldWidget(field, NamedImageWidget(request))
