# -*- coding: utf-8 -*-

from collective.cover.testing import FUNCTIONAL_TESTING
from collective.cover.testing import ROBOT_TESTING
from plone.testing import layered

import os
import robotsuite
import unittest

dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test_') and f.endswith('.robot')]

# FIXME: https://github.com/collective/collective.cover/issues/285
tests.remove('test_contentchooser_search_tab.robot')

# TODO: refactor and rename all Robot tests
_tests = [f for f in files if f.startswith('robot_') and f.endswith('.txt')]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite(t), layer=ROBOT_TESTING)
        for t in tests
    ])
    suite.addTests([
        layered(robotsuite.RobotTestSuite(t), layer=FUNCTIONAL_TESTING)
        for t in _tests
    ])
    return suite
