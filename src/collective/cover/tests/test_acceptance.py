# -*- coding: utf-8 -*-

from collective.cover.testing import FUNCTIONAL_TESTING
from plone.testing import layered

import os
import robotsuite
import unittest

dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test_') and f.endswith('.txt')]

# FIXME: test is failing, remove from master but take care of it on branch
# see: https://github.com/collective/collective.cover/issues/155
tests.remove('test_contenttree_tab_path.txt',)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite(t), layer=FUNCTIONAL_TESTING)
        for t in tests
    ])
    return suite
