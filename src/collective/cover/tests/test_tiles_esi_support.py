# -*- coding: utf-8 -*-

import unittest2 as unittest
import doctest
from plone.testing import layered

from collective.cover.testing import FUNCTIONAL_TESTING


def test_suite():
    return unittest.TestSuite((
        layered(doctest.DocFileSuite('test_tiles_esi_support.rst'),
                layer=FUNCTIONAL_TESTING),
    ))
