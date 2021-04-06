# -*- coding: utf-8 -*-
from collective.cover.testing import ROBOT_TESTING
from plone.testing import layered

import os
import robotsuite
import unittest


dirname = os.path.dirname(__file__)
files = os.listdir(dirname)

# FIXME: skip RobotFramework tests in Plone 5
tests = []

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
