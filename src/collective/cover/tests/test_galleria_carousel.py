# -*- coding: utf-8 -*-

from collective.cover.testing import GALLERIA_FUNCTIONAL_TESTING
from plone.testing import layered

import os
import robotsuite
import unittest

dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = ['testgalleria_carousel_tile.robot']


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            robotsuite.RobotTestSuite(t, noncritical=['Expected Failure']),
            layer=GALLERIA_FUNCTIONAL_TESTING)
        for t in tests
    ])
    return suite
