# -*- coding: utf-8 -*-

from five import grok

from zope.component import getUtility

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from plone.registry.interfaces import IRegistry

from collective.composition.controlpanel import ICompositionSettings


class LayoutVocabulary(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'collective.composition.vocabularies.layouts')

    def __call__(self, context):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICompositionSettings)

        items = [SimpleTerm(value=i, title=i) for i in settings.layouts]
        return SimpleVocabulary(items)
