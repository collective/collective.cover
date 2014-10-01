# -*- coding: utf-8 -*-

from App.Common import package_home
from collective.cover import _
from collective.cover.layout import Deco16Grid
from PIL import Image
from PIL import ImageChops
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from StringIO import StringIO
from zope.component import getGlobalSiteManager

import os
import pkg_resources
import random

PLONE_VERSION = pkg_resources.require('Plone')[0].version

try:
    pkg_resources.get_distribution('Products.PloneFormGen')
except pkg_resources.DistributionNotFound:
    HAS_PFG = False
else:
    HAS_PFG = True

ALL_CONTENT_TYPES = [
    'Collection',
    'Document',
    'File',
    'Image',
    'Link',
    'News Item',
]


def loadFile(name, size=0):
    """Load file from testing directory
    """
    path = os.path.join(package_home(globals()), 'tests/input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data


def generate_jpeg(width, height):
    # Mandelbrot fractal
    # FB - 201003254
    # drawing area
    xa = -2.0
    xb = 1.0
    ya = -1.5
    yb = 1.5
    maxIt = 25  # max iterations allowed
    # image size
    image = Image.new('RGB', (width, height))
    c = complex(random.random() * 2.0 - 1.0, random.random() - 0.5)

    for y in range(height):
        zy = y * (yb - ya) / (height - 1) + ya
        for x in range(width):
            zx = x * (xb - xa) / (width - 1) + xa
            z = complex(zx, zy)
            for i in range(maxIt):
                if abs(z) > 2.0:
                    break
                z = z * z + c
            r = i % 4 * 64
            g = i % 8 * 32
            b = i % 16 * 16
            image.putpixel((x, y), b * 65536 + g * 256 + r)

    output = StringIO()
    image.save(output, format='PNG')
    return output


def images_are_equal(str1, str2):
    im1 = StringIO()
    im2 = StringIO()
    im1.write(str1)
    im1.seek(0)
    im2.write(str2)
    im2.seek(0)
    return ImageChops.difference(Image.open(im1), Image.open(im2)).getbbox() is None


class Bootstrap3(Deco16Grid):
    ncolumns = 12
    title = _(u'Bootstrap 3')

    def columns_formatter(self, columns):
        prefix = 'col-md-'
        for column in columns:
            width = column['data']['column-size'] if 'data' in column else 1
            column['class'] = self.column_class + ' ' + (prefix + str(width))

        return columns


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # XXX: do not install (yet) PFG in Plone 5
        if HAS_PFG and PLONE_VERSION < '5.0':
            import Products.PloneFormGen
            self.loadZCML(package=Products.PloneFormGen)
            z2.installProduct(app, 'Products.PloneFormGen')

        # Load ZCML
        import collective.cover
        self.loadZCML(package=collective.cover)

        if 'virtual_hosting' not in app.objectIds():
            # If ZopeLite was imported, we have no default virtual
            # host monster
            from Products.SiteAccess.VirtualHostMonster \
                import manage_addVirtualHostMonster
            manage_addVirtualHostMonster(app, 'virtual_hosting')

    def setUpPloneSite(self, portal):
        # XXX: do not install (yet) PFG in Plone 5
        if HAS_PFG and PLONE_VERSION < '5.0':
            self.applyProfile(portal, 'Products.PloneFormGen:default')

        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.cover:default')
        self.applyProfile(portal, 'collective.cover:testfixture')
        portal['my-image'].setImage(generate_jpeg(50, 50))
        portal['my-image'].reindexObject()
        portal['my-image1'].setImage(generate_jpeg(50, 50))
        portal['my-image1'].reindexObject()
        portal['my-image2'].setImage(generate_jpeg(50, 50))
        portal['my-image2'].reindexObject()
        portal['my-file'].setFile(loadFile('lorem_ipsum.txt'))
        portal['my-file'].reindexObject()
        portal['my-news-item'].setImage(generate_jpeg(50, 50))
        portal['my-news-item'].reindexObject()
        portal_workflow = portal.portal_workflow
        portal_workflow.setChainForPortalTypes(
            ['Collection', 'Event'], ['simple_publication_workflow'])

        # Prevent kss validation errors in Plone 4.2
        portal_kss = getattr(portal, 'portal_kss', None)
        if portal_kss:
            portal_kss.getResource('++resource++plone.app.z3cform').setEnabled(False)

FIXTURE = Fixture()


class MultipleGridsFixture(Fixture):

    defaultBases = (FIXTURE,)

    def setUpZope(self, app, configurationContext):
        newgrid = Bootstrap3()
        sm = getGlobalSiteManager()
        sm.registerUtility(newgrid, name='bootstrap3')


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='collective.cover:Integration',
)

MULTIPLE_GRIDS_FIXTURE = MultipleGridsFixture()
MULTIPLE_GRIDS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MULTIPLE_GRIDS_FIXTURE,),
    name='collective.cover:MultipleGridsIntegration',
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE),
    name='collective.cover:Functional',
)

ROBOT_TESTING = FunctionalTesting(
    bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name='collective.cover:Robot')
