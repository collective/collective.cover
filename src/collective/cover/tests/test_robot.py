# -*- coding: utf-8 -*-

from collective.cover.testing import ROBOT_TESTING
from plone.testing import layered

import os
import robotsuite
import unittest

dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test_') and f.endswith('.robot')]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            robotsuite.RobotTestSuite(t, noncritical=['Expected Failure']),
            layer=ROBOT_TESTING)
        for t in tests
    ])
    return suite
