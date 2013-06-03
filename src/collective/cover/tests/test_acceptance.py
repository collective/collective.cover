# -*- coding: utf-8 -*-

from collective.cover.testing import FUNCTIONAL_TESTING
from plone.testing import layered

import os
import robotsuite
import unittest

dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test_') and f.endswith('.txt')]

# TODO: rename all tests from .txt to .robot
tests.append('test_banner_tile.robot')

# FIXME: https://github.com/collective/collective.cover/issues/202
tests.remove('test_carousel_tile.txt')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite(t), layer=FUNCTIONAL_TESTING)
        for t in tests
    ])
    return suite
