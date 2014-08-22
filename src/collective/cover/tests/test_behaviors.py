# -*- coding: utf-8 -*-
from collective.cover.behaviors.interfaces import IBackgroundImage
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility

import unittest


class BackgroundImageTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING
    name = 'collective.cover.behaviors.interfaces.IBackgroundImage'

    def _enable_background_image_behavior(self):
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        behaviors = list(fti.behaviors)
        behaviors.append(self.name)
        fti.behaviors = tuple(behaviors)

    def _disable_background_image_behavior(self):
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        behaviors = list(fti.behaviors)
        behaviors.remove(self.name)
        fti.behaviors = tuple(behaviors)

    def setUp(self):
        self.portal = self.layer['portal']

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'test')

        self._enable_background_image_behavior()
        self.cover = api.content.create(
            self.folder, 'collective.cover.content', 'c1')

    def test_background_registration(self):
        registration = queryUtility(IBehavior, name=self.name)
        self.assertIsNotNone(registration)

    def test_background_in_cover(self):
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        self.assertIn(self.name, fti.behaviors)

    @unittest.expectedFailure  # FIXME
    def test_adapt_content(self):
        background = IBackgroundImage(self.cover, None)
        self.assertIsNotNone(background)

        self._disable_background_image_behavior()
        cover = api.content.create(
            self.folder, 'collective.cover.content', 'c2')
        background = IBackgroundImage(cover, None)
        self.assertIsNone(background)

    def test_background_image_field(self):
        from plone.namedfile.file import NamedImage
        background = IBackgroundImage(self.cover)
        self.assertIsNone(background.background_image)
        background.background_image = NamedImage()
        self.assertIsInstance(background.background_image, NamedImage)
