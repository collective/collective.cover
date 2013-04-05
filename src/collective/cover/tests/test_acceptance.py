import unittest

import robotsuite

from plone.testing import layered

from collective.cover.testing import FUNCTIONAL_TESTING

import pkg_resources
PLONE_VERSION = pkg_resources.require("Plone")[0].version


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("test_cover.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_layout.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_basic_tile.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_contenttree_tab.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_contenttree_tab_path.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_collection_tile.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_embed_tile.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_file_tile.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_image_tile.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_list_tile.txt"),
                layer=FUNCTIONAL_TESTING),
        layered(robotsuite.RobotTestSuite("test_locked_cover.txt"),
                layer=FUNCTIONAL_TESTING),
    ])
    # FIXME: test randomly failing under Plone 4.3.x
    #        see https://github.com/collective/collective.cover/issues/155
    if '4.3' not in PLONE_VERSION:
        suite.addTests([
            layered(robotsuite.RobotTestSuite("test_screenlet_search_tab.txt"),
                    layer=FUNCTIONAL_TESTING),
        ])
    return suite
