# -*- coding: utf-8 -*-
import os
import random
from StringIO import StringIO
from PIL import Image, ImageChops

from App.Common import package_home

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing.z2 import ZSERVER_FIXTURE
from plone.testing.z2 import installProduct


def loadImage(name, size=0):
    """Load image from testing directory
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
    image = Image.new("RGB", (width, height))
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
    image.save(output, format="PNG")
    return output.getvalue()


def images_are_equal(str1, str2):
    im1 = StringIO()
    im2 = StringIO()
    im1.write(str1)
    im1.seek(0)
    im2.write(str2)
    im2.seek(0)
    return ImageChops.difference(Image.open(im1), Image.open(im2)).getbbox() is None


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import Products.PloneFormGen
        self.loadZCML(package=Products.PloneFormGen)
        installProduct(app, 'Products.PloneFormGen')
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
        portal['my-image1'].setImage(generate_jpeg(50, 50))
        portal['my-image2'].setImage(generate_jpeg(50, 50))
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
