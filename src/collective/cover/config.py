# -*- coding: utf-8 -*-
from collective.cover.tiles.configuration import ANNOTATIONS_KEY_PREFIX as CONFIGURATION_PREFIX
from collective.cover.tiles.permissions import ANNOTATIONS_KEY_PREFIX as PERMISSIONS_PREFIX
from plone import api
from plone.tiles.data import ANNOTATIONS_KEY_PREFIX as DATA_PREFIX


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
    'News Item',
]

IS_PLONE_5 = api.env.plone_version().startswith('5')

DEFAULT_GRID_SYSTEM = 'bootstrap3' if IS_PLONE_5 else 'deco16_grid'

_ = u'[{{"type": "row", "children": [{{"type": "group", "column-size": {size}, "roles": ["Manager"]}}]}}]'
_SIZE = 12 if IS_PLONE_5 else 16
EMPTY_LAYOUT = _.format(size=_SIZE)

# z3c.form.widget.SequenceWidget used for css_class field
# has a default null value of '--NOVALUE--'
# In case that no value was set to that field
# we need to detect it and use it
DEFAULT_SEQUENCEWIDGET_VALUE = '--NOVALUE--'

ANNOTATION_PREFIXES = (DATA_PREFIX, CONFIGURATION_PREFIX, PERMISSIONS_PREFIX)
