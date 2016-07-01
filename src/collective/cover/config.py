# -*- coding: utf-8 -*-
from plone import api

PROJECTNAME = 'collective.cover'

# by default, all cover tiles will be available on layouts
DEFAULT_AVAILABLE_TILES = [
    'collective.cover.banner',
    'collective.cover.basic',
    'collective.cover.calendar',
    'collective.cover.carousel',
    'collective.cover.collection',
    'collective.cover.contentbody',
    'collective.cover.embed',
    'collective.cover.file',
    'collective.cover.list',
    'collective.cover.richtext',
]

# by default, all standard content types will be searchable
DEFAULT_SEARCHABLE_CONTENT_TYPES = [
    'Collection',
    'Document',
    'File',
    'Image',
    'Link',
    'News Item'
]

PLONE_VERSION = api.env.plone_version()

DEFAULT_GRID_SYSTEM = 'deco16_grid' if PLONE_VERSION < '5.0' else 'bootstrap3'

# z3c.form.widget.SequenceWidget used for css_class field
# has a default null value of '--NOVALUE--'
# In case that no value was set to that field
# we need to detect it and use it
DEFAULT_SEQUENCEWIDGET_VALUE = '--NOVALUE--'
