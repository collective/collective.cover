# -*- coding: utf-8 -*-
# TODO: this module must be removed in 1.4 release
from collective.cover.grid import BaseGrid  # noqa
from zope import deprecation


deprecation.deprecated('BaseGrid', 'moved to collective.cover.grids')
