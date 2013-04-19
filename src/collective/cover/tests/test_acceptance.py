# -*- coding: utf-8 -*-

from collective.cover.testing import FUNCTIONAL_TESTING
from plone.testing import layered

import robotsuite
import unittest

import pkg_resources
PLONE_VERSION = pkg_resources.require("Plone")[0].version

tests = [
    'test_basic_tile.txt',
    'test_collection_tile.txt',
    'test_contentchooser_search_tab.txt',
    'test_contenttree_tab.txt',
    'test_contenttree_tab_path.txt',
    'test_cover.txt',
    'test_embed_tile.txt',
    'test_file_tile.txt',
    'test_image_tile.txt',
    'test_layout.txt',
    'test_list_tile.txt',
    'test_locked_cover.txt',
    'test_issue_59.txt',
]

# FIXME: test randomly failing under Plone 4.3.x
#        see https://github.com/collective/collective.cover/issues/155
if '4.3' in PLONE_VERSION:
    tests.remove('test_contentchooser_search_tab.txt',)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite(t), layer=FUNCTIONAL_TESTING)
        for t in tests
    ])
    return suite
