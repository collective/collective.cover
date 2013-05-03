# -*- coding: utf-8 -*-

from collective.cover.testing import FUNCTIONAL_TESTING
from plone.testing import layered

import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        layered(doctest.DocFileSuite('test_tiles_esi_support.rst'),
                layer=FUNCTIONAL_TESTING),
    ))
