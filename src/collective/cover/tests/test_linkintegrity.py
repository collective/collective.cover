# -*- coding: utf-8 -*-

from collective.cover.testing import Fixture
from collective.cover.testing import generate_jpeg
from collective.cover.tests import linkintegrity_docs as docs
from plone.app.testing import FunctionalTesting
from plone.app.testing import setRoles
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing.interfaces import SITE_OWNER_PASSWORD
from plone.app.testing.interfaces import TEST_USER_ID
from plone.app.textfield import RichText
from plone.dexterity.fti import DexterityFTI
from plone.testing import z2
from Products.PloneTestCase import PloneTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite
from zope.interface import Interface

import os
import unittest


class IMyDexterityItem(Interface):
    text = RichText(title=u'Text')

PloneTestCase.setupPloneSite()

from ZPublisher.HTTPRequest import HTTPRequest
set_orig = HTTPRequest.set

from zope.testing import doctest
OPTIONFLAGS = (
    doctest.REPORT_ONLY_FIRST_FAILURE |
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE
)


class LinkintegrityFixture(Fixture):

    def setUpZope(self, app, configurationContext):
        super(LinkintegrityFixture, self).setUpZope(app, configurationContext)
        import plone.app.linkintegrity
        self.loadZCML(package=plone.app.linkintegrity)
        z2.installProduct(app, 'plone.app.linkintegrity')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        # self.applyProfile(portal, 'plone.app.linkintegrity:default')
        super(LinkintegrityFixture, self).setUpPloneSite(portal)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        fti = DexterityFTI('My Dexterity Item')
        portal.portal_types._setObject('My Dexterity Item', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.schema = 'collective.cover.tests.test_linkintegrity.IMyDexterityItem'
        fti.behaviors = ('plone.app.referenceablebehavior.referenceable.IReferenceable',)
        fti = DexterityFTI('Non referenciable Dexterity Item')
        portal.portal_types._setObject('Non referenciable Dexterity Item', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.schema = 'collective.cover.tests.test_linkintegrity.IMyDexterityItem'
        # Create some dexterity items to test with it
        portal.invokeFactory(
            'My Dexterity Item', id='dexterity_item1', title='Dexterity Item 1')
        portal.invokeFactory(
            'My Dexterity Item', id='dexterity_item2', title='Dexterity Item 2')
        portal.invokeFactory(
            'Non referenciable Dexterity Item',
            id='nonreferenciable_dexterity_item1',
            title='Non referenciable Dexterity Item 1'
        )
        portal.invokeFactory(
            'Non referenciable Dexterity Item',
            id='nonreferenciable_dexterity_item2',
            title='Non referenciable Dexterity Item 2'
        )
        # Create an AT Image
        image = generate_jpeg(50, 50)
        portal.invokeFactory(
            'Image', id='image1', title='Test Image 1', image=image)
        portal.invokeFactory('collective.cover.content', 'cover1')
        # Documents
        text = '<html> <body> a test page </body> </html>'
        portal.invokeFactory(
            'Document', id='doc1', title='Test Page 1', text=text)
        text = '<html> <body> another test page </body> </html>'
        portal.invokeFactory(
            'Document', id='doc2', title='Test Page 2', text=text)
        text = '<html> <body> a test page in a subfolder </body> </html>'
        portal.invokeFactory('Folder', id='folder1', title='Test Folder 1')
        portal.folder1.invokeFactory(
            'Document', id='doc3', title='Test Page 3', text=text)

LINKINTEGRITY_FIXTURE = LinkintegrityFixture()
LINKINTEGRITY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(LINKINTEGRITY_FIXTURE,),
    name='collective.cover:LinkintegrityFunctional',
)


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
        self.browser = z2.Browser(self.layer['app'])
        self.tile = self.portal.cover1.restrictedTraverse(
            '@@{0}/{1}'.format('collective.cover.richtext', 'test-richtext-tile'))
        self.browser.handleErrors = True
        self.browser.addHeader(
            'Authorization', 'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD))

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

dirname = os.path.dirname(__file__) + '/linkintegrity_docs'
files = os.listdir(dirname)
tests = [f for f in files if f.startswith('test') and f.endswith('.txt')]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        FunctionalDocFileSuite(
            t,
            optionflags=OPTIONFLAGS,
            package=docs.__name__,
            test_class=LinkIntegrityFunctionalTestCase)
        for t in tests
    ])
    return suite
