# -*- coding: utf-8 -*-

"""

XXX:

This module for helping in our test is really ugly but we didn't have a better
option.

The idea of the test is to raise an exception to force the javascript to print

    "Internal Server Error"

on the tile. An earlier simple test was made, that consisted of inserting an
invalid image (we took a zip file and changed it's extension to jpg) in the
tile and waiting for "Internal Server Error" string. So far, so good. It
perfectly worked when using bin/instance to add this image to a tile.

The problem is: different behaviors were happening when using bin/instance for
this manual test and when using bin/test. An issue was opened in

    https://github.com/collective/collective.cover/issues/586

to try to solve this difference in behavior when using plone.app.testing
machinery.

Until this issue is not resolved, there's no other way to force an exception in
a tile other than using a patch like the one below. At least this is a keyword
in this library and perfectly documented in test_basic_tile.robot.

When issue 586 is solved, this patch can be removed and a new test adding an
invalid image can be created to test the "Internal Server Error" string.

"""

from collective.cover.tiles.basic import BasicTile


ORIGINAL_POPULATE_WITH_OBJECT = BasicTile.populate_with_object


def apply_patch_populate_with_object():

    def patched_populate_with_object(self, obj):
        raise Exception('Testing Server Error.')

    BasicTile.populate_with_object = patched_populate_with_object


def remove_patch_populate_with_object():
    BasicTile.populate_with_object = ORIGINAL_POPULATE_WITH_OBJECT
