import unittest

import robotsuite

from plone.testing import layered

from collective.cover.testing import FUNCTIONAL_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("test_cover.txt"),
                layer=FUNCTIONAL_TESTING),
    ])
    return suite
