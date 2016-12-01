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
from collective.cover.testing import DEXTERITY_ONLY
from collective.cover.testing import ROBOT_TESTING
from plone import api
from plone.testing import layered

import os
import robotsuite
import unittest


PLONE_VERSION = api.env.plone_version()

dirname = os.path.dirname(__file__)
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test_') and f.endswith('.robot')]

noncritical = ['Expected Failure', 'Mandelbug']

# XXX: Link integrity tests fail under Plone 4.2 and under
#      Plone 4.3 with plone.app.contenttypes installed
#      https://github.com/collective/collective.cover/issues/615
if PLONE_VERSION.startswith('4.2') or \
        (PLONE_VERSION.startswith('4.3') and DEXTERITY_ONLY):
    noncritical.append('issue_615')

# FIXME: https://github.com/collective/collective.cover/issues/637
if PLONE_VERSION.startswith('4.3') and DEXTERITY_ONLY:
    noncritical.append('issue_637')

# FIXME: skip RobotFramework tests in Plone 5
if PLONE_VERSION.startswith('5'):
    tests = []


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            robotsuite.RobotTestSuite(t, noncritical=noncritical),
            layer=ROBOT_TESTING)
        for t in tests
    ])
    return suite
