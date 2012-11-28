# -*- coding: utf-8 -*-
import os

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

FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='collective.cover:Integration',
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, ZSERVER_FIXTURE),
    name='collective.cover:Functional',
)
