# -*- coding: utf-8 -*-

from collective.cover.testing import FUNCTIONAL_TESTING
from plone.testing import layered

import os
import pkg_resources
import robotsuite
import unittest

PLONE_VERSION = pkg_resources.require("Plone")[0].version

dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test_') and f.endswith('.txt')]

# TODO: rename all tests from .txt to .robot
tests.append('test_banner_tile.robot')

# FIXME: https://github.com/collective/collective.cover/issues/281
if '4.2' in PLONE_VERSION:
    tests.remove('test_collection_tile.txt')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite(t), layer=FUNCTIONAL_TESTING)
        for t in tests
    ])
    return suite
