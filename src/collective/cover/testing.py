# -*- coding: utf-8 -*-
from collective.cover.tests.utils import create_standard_content_for_tests
from collective.cover.tests.utils import set_file_field
from collective.cover.tests.utils import set_image_field
from PIL import Image
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing.zope import WSGI_SERVER

import os
import random
import six


ALL_CONTENT_TYPES = [
    "Collection",
    "Document",
    "File",
    "Image",
    "Link",
    "News Item",
]

zptlogo = (
    b"GIF89a\x10\x00\x10\x00\xd5\x00\x00\xff\xff\xff\xff\xff\xfe\xfc\xfd\xfd"
    b"\xfa\xfb\xfc\xf7\xf9\xfa\xf5\xf8\xf9\xf3\xf6\xf8\xf2\xf5\xf7\xf0\xf4\xf6"
    b"\xeb\xf1\xf3\xe5\xed\xef\xde\xe8\xeb\xdc\xe6\xea\xd9\xe4\xe8\xd7\xe2\xe6"
    b"\xd2\xdf\xe3\xd0\xdd\xe3\xcd\xdc\xe1\xcb\xda\xdf\xc9\xd9\xdf\xc8\xd8\xdd"
    b"\xc6\xd7\xdc\xc4\xd6\xdc\xc3\xd4\xda\xc2\xd3\xd9\xc1\xd3\xd9\xc0\xd2\xd9"
    b"\xbd\xd1\xd8\xbd\xd0\xd7\xbc\xcf\xd7\xbb\xcf\xd6\xbb\xce\xd5\xb9\xcd\xd4"
    b"\xb6\xcc\xd4\xb6\xcb\xd3\xb5\xcb\xd2\xb4\xca\xd1\xb2\xc8\xd0\xb1\xc7\xd0"
    b"\xb0\xc7\xcf\xaf\xc6\xce\xae\xc4\xce\xad\xc4\xcd\xab\xc3\xcc\xa9\xc2\xcb"
    b"\xa8\xc1\xca\xa6\xc0\xc9\xa4\xbe\xc8\xa2\xbd\xc7\xa0\xbb\xc5\x9e\xba\xc4"
    b"\x9b\xbf\xcc\x98\xb6\xc1\x8d\xae\xbaFgs\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06z@\x80pH,\x12k\xc8$\xd2f\x04"
    b"\xd4\x84\x01\x01\xe1\xf0d\x16\x9f\x80A\x01\x91\xc0ZmL\xb0\xcd\x00V\xd4"
    b"\xc4a\x87z\xed\xb0-\x1a\xb3\xb8\x95\xbdf8\x1e\x11\xca,MoC$\x15\x18{"
    b"\x006}m\x13\x16\x1a\x1f\x83\x85}6\x17\x1b $\x83\x00\x86\x19\x1d!%)\x8c"
    b"\x866#'+.\x8ca`\x1c`(,/1\x94B5\x19\x1e\"&*-024\xacNq\xba\xbb\xb8h\xbeb"
    b"\x00A\x00;"
)


def load_file(name):
    """Load file from testing directory."""
    path = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(path, "tests/input", name)
    with open(filename, "r") as f:
        data = f.read()
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
    c = complex(random.random() * 2.0 - 1.0, random.random() - 0.5)  # nosec

    for y in range(height):
        zy = y * (yb - ya) // (height - 1) + ya
        for x in range(width):
            zx = x * (xb - xa) // (width - 1) + xa
            z = complex(zx, zy)
            for i in range(maxIt):
                if abs(z) > 2.0:
                    break
                z = z * z + c
            r = i % 4 * 64
            g = i % 8 * 32
            b = i % 16 * 16
            image.putpixel((x, y), b * 65536 + g * 256 + r)

    output = six.BytesIO()
    image.save(output, format="PNG")
    return output


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.app.contenttypes

        self.loadZCML(package=plone.app.contenttypes)

        import collective.cover

        self.loadZCML(package=collective.cover)

        if "virtual_hosting" not in app.objectIds():
            # If ZopeLite was imported, we have no default virtual
            # host monster
            from Products.SiteAccess.VirtualHostMonster import (
                manage_addVirtualHostMonster,
            )

            manage_addVirtualHostMonster(app, "virtual_hosting")

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, "plone.app.contenttypes:default")

        self.applyProfile(portal, "collective.cover:default")
        self.applyProfile(portal, "collective.cover:testfixture")

        # setup test content
        create_standard_content_for_tests(portal)
        set_file_field(portal["my-file"], load_file("lorem_ipsum.txt"))
        set_image_field(portal["my-image"], generate_jpeg(50, 50))
        set_image_field(portal["my-image1"], generate_jpeg(50, 50))
        set_image_field(portal["my-image2"], generate_jpeg(50, 50))
        set_image_field(portal["my-news-item"], generate_jpeg(50, 50))

        portal_workflow = portal.portal_workflow
        portal_workflow.setChainForPortalTypes(
            ["Collection", "Event"], ["simple_publication_workflow"]
        )


FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="collective.cover:Integration",
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER),
    name="collective.cover:Functional",
)

ROBOT_TESTING = FunctionalTesting(
    bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, WSGI_SERVER),
    name="collective.cover:Robot",
)
