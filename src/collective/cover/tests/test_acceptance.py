import unittest

import robotsuite

from plone.testing import layered

from collective.cover.testing import FUNCTIONAL_TESTING


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
        layered(robotsuite.RobotTestSuite("test_screenlet_search_tab.txt"),
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
    return suite
