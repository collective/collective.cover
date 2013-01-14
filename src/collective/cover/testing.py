# -*- coding: utf-8 -*-
import os
import urllib2

from App.Common import package_home

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing.z2 import ZSERVER_FIXTURE


def loadImage(name, size=0):
    """Load image from testing directory
    """
    path = os.path.join(package_home(globals()), 'tests/input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data


def generate_jpeg(width, height):
    url = 'http://lorempixel.com/%d/%d/' % (width, height)
    return urllib2.urlopen(url).read()


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.cover
        self.loadZCML(package=collective.cover)
        # XXX: https://github.com/collective/collective.cover/issues/81
        #import plone.app.imagetile
        #self.loadZCML(package=plone.app.imagetile)
        #import plone.app.texttile
        #self.loadZCML(package=plone.app.imagetile)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.cover:default')
        self.applyProfile(portal, 'collective.cover:testfixture')
        portal['my-image'].setImage(loadImage('canoneye.jpg'))
        portal['my-image1'].setImage(generate_jpeg(100, 100))
        portal['my-image2'].setImage(generate_jpeg(100, 100))
        portal['my-file'].setFile(loadImage('canoneye.jpg'))
        portal['my-file'].reindexObject()
        portal_workflow = portal.portal_workflow
        portal_workflow.setChainForPortalTypes(['Collection'],
                                               ['plone_workflow'],)


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='collective.cover:Integration',
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, ZSERVER_FIXTURE),
    name='collective.cover:Functional',
)
