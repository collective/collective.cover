# -*- coding: utf-8 -*-
# setup tests with all doctests found in docs/

from collective.cover.testing import LINKINTEGRITY_FUNCTIONAL_TESTING
from collective.cover.tests import linkintegrity_docs as docs
from os import walk
from os.path import join, split, abspath, dirname
from plone.app.testing.interfaces import (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
from plone.app.textfield import RichText
from plone.testing.z2 import Browser
from Products.PloneTestCase import PloneTestCase
from re import compile
from sys import argv
from Testing.ZopeTestCase import FunctionalDocFileSuite
from unittest import TestSuite
from zope.interface import Interface

import unittest


class IMyDexterityItem(Interface):
    text = RichText(title=u'Text')


PloneTestCase.setupPloneSite()

from ZPublisher.HTTPRequest import HTTPRequest
set_orig = HTTPRequest.set

from zope.testing import doctest
OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


class LinkIntegrityFunctionalTestCase(unittest.TestCase):

    layer = LINKINTEGRITY_FUNCTIONAL_TESTING

    def setUp(self):
        # HTTPRequest's 'set' function is set to it's original implementation
        # at the start of each new test, since otherwise the below monkey
        # patch will apply to all remaining tests (and break them);  see
        # comment below in 'disableEventCountHelper'
        HTTPRequest.set = set_orig
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.layer['app'])
        self.tile = self.portal.cover1.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.richtext', 'test-richtext-tile'))
        self.browser.handleErrors = True
        self.browser.addHeader('Authorization', 'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD))

    def setStatusCode(self, key, value):
        from ZPublisher import HTTPResponse
        HTTPResponse.status_codes[key.lower()] = value

    def setText(self, obj, text, **kw):
        kw['text'] = '<html> <body> %s </body> </html>' % text
        return obj.processForm(values=kw)

    def disableEventCountHelper(self):
        # so here's yet another monkey patch ;), but only to avoid having
        # to change almost all the tests after introducing the setting of
        # the helper value in 'folder_delete', which prevents presenting
        # the user with multiple confirmation forms;  this patch prevents
        # setting the value and is meant to disable this optimization in
        # some of the tests written so far, thereby not invalidating them...
        def set(self, key, value, set_orig=set_orig):
            if key == 'link_integrity_events_to_expect':
                value = 0
            set_orig(self, key, value)
        HTTPRequest.set = set


# we check argv to enable testing of explicitely named doctests
if '-t' in argv:
    pattern = compile('.*\.(txt|rst)$')
else:
    pattern = compile('^test.*\.(txt|rst)$')


def test_suite():
    suite = TestSuite()
    docs_dir = abspath(dirname(docs.__file__)) + '/'
    for path, dirs, files in walk(docs_dir):
        for name in files:
            relative = join(path, name)[len(docs_dir):]
            if not '.svn' in split(path) and pattern.search(name):
                suite.addTest(FunctionalDocFileSuite(relative,
                              optionflags=OPTIONFLAGS,
                              package=docs.__name__,
                              test_class=LinkIntegrityFunctionalTestCase))
    return suite
