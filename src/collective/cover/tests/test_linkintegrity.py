# setup tests with all doctests found in docs/

import pkg_resources
from zope.interface import Interface
from plone.app.linkintegrity.parser import extractLinks
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase import PloneTestCase
from unittest import TestSuite, TestCase, makeSuite
from os.path import join, split, abspath, dirname
from os import walk
from re import compile
from sys import argv
from collective.cover.tests import linkintegrity_docs as docs
from plone.app.linkintegrity.tests import layer, utils


try:
    pkg_resources.get_distribution('plone.app.referenceablebehavior')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
    pass
else:
    HAS_DEXTERITY = True
    from plone.dexterity.fti import DexterityFTI
    from plone.app.textfield import RichText
    from plone.app.textfield.value import RichTextValue
    class IMyDexterityItem(Interface):
        text = RichText(title=u'Text')

PloneTestCase.setupPloneSite()

from ZPublisher.HTTPRequest import HTTPRequest
set_orig = HTTPRequest.set

from zope.testing import doctest
OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


class LinkIntegrityFunctionalTestCase(PloneTestCase.FunctionalTestCase):

    layer = layer.integrity

    def afterSetUp(self):
        """ create some sample content to test with """
        # HTTPRequest's 'set' function is set to it's original implementation
        # at the start of each new test, since otherwise the below monkey
        # patch will apply to all remaining tests (and break them);  see
        # comment below in 'disableEventCountHelper'
        HTTPRequest.set = set_orig
        self.setRoles(('Manager',))
        fti = DexterityFTI('My Dexterity Item')
        self.portal.portal_types._setObject('My Dexterity Item', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.schema = 'plone.app.linkintegrity.tests.test_dexterity.IMyDexterityItem'
        fti.behaviors = ('plone.app.referenceablebehavior.referenceable.IReferenceable',)
        fti = DexterityFTI('Non referenciable Dexterity Item')
        self.portal.portal_types._setObject('Non referenciable Dexterity Item', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.schema = 'plone.app.linkintegrity.tests.test_dexterity.IMyDexterityItem'
        self.portal.invokeFactory('My Dexterity Item', id='dexterity_item1',
                                  title='Dexterity Item 1')
        self.portal.invokeFactory('My Dexterity Item', id='dexterity_item2',
                                  title='Dexterity Item 2')
        self.portal.invokeFactory('Non referenciable Dexterity Item',
                             id='nonreferenciable_dexterity_item1',
                             title='Non referenciable Dexterity Item 1')
        self.portal.invokeFactory('Non referenciable Dexterity Item',
                             id='nonreferenciable_dexterity_item2',
                             title='Non referenciable Dexterity Item 2')
        
    def getBrowser(self, loggedIn=False):
        """ instantiate and return a testbrowser for convenience """
        return utils.getBrowser(loggedIn)

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


class LinkIntegrityTestCase(TestCase):

    def testHandleParserException(self):
        self.assertEqual(extractLinks('<foo\'d>'), ())
        self.assertEqual(extractLinks('<a href="http://foo.com">foo</a><bar\'d>'), ('http://foo.com',))


# we check argv to enable testing of explicitely named doctests
if '-t' in argv:
    pattern = compile('.*\.(txt|rst)$')
else:
    pattern = compile('^test.*\.(txt|rst)$')


def test_suite():
    suite = TestSuite([
        makeSuite(LinkIntegrityTestCase),
    ])
    if HAS_DEXTERITY:    
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
