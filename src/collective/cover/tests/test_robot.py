# -*- coding: utf-8 -*-
"""Setup RobotFramework tests.
We have 3 kinds of expected failures:
Expected Failure
    We know they are failing and need some work to be fixed.
Mandelbug
    Their behaviour is chaotic and they are hard to fix.
Issue related
    They are failing under certain reproducible circunstances.
"""
from collective.cover.testing import ROBOT_TESTING
from plone.testing import layered

import os
import robotsuite
import unittest


dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith("test_") and f.endswith(".robot")]

noncritical = ["Expected Failure", "Mandelbug"]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            layered(
                robotsuite.RobotTestSuite(t, noncritical=noncritical),
                layer=ROBOT_TESTING,
            )
            for t in tests
        ]
    )
    return suite
