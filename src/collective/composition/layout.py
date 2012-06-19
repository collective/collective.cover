# -*- coding: utf-8 -*-

from five import grok

from zope.interface import Interface

from zope.component import getAdapters

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class ICompositionLayout(Interface):
    """
    layout for composable page
    """


class LayoutVocabulary(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'collective.composition.vocabularies.layouts')

    def __call__(self, context):
        items = []
        layouts = getAdapters([context], ICompositionLayout)
        items = [(l[1].description, l[0]) for l in layouts]
        items.sort()
        items = [SimpleTerm(i[1], i[1], i[0]) for i in items]
        return SimpleVocabulary(items)


class CompositionLayout(grok.Adapter):
    grok.provides(ICompositionLayout)
    grok.context(Interface)
    grok.name(u'collective.composition.layouts.default')

    description = "Single column layout"
    column_class = "full-column"

    LAYOUT = """
    <div id="columns">
      <ul id="column1" class="column full-column">
      </ul>
    </div>
    """

    def render(self):
        return self.LAYOUT

    @property
    def columns(self):
        return ['column1']


class TwoColumnLayout(CompositionLayout):
    grok.name(u'collective.composition.layouts.twocolumns')

    description = "Two column flexible layout"
    column_class = "flex-half-column"

    LAYOUT = """
    <div id="columns">
      <ul id="column1" class="column flex-half-column">
      </ul>
      <ul id="column2" class="column flex-half-column">
      </ul>
    </div>
    """

    @property
    def columns(self):
        return ['column1', 'column2']


class ThreeColumnLayout(CompositionLayout):
    grok.name(u'collective.composition.layouts.threecolumns')

    description = "Three column flexible layout"
    column_class = "flex-third-column"

    LAYOUT = """
    <div id="columns">
      <ul id="column1" class="column flex-third-column">
      </ul>
      <ul id="column2" class="column flex-third-column">
      </ul>
      <ul id="column3" class="column flex-third-column">
      </ul>
    </div>
    """

    @property
    def columns(self):
        return ['column1', 'column2', 'column3']
