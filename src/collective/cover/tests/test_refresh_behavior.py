# -*- coding: utf-8 -*-
from collective.cover.behaviors.interfaces import IRefresh
from collective.cover.interfaces import ICoverLayer
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.schema import SchemaInvalidatedEvent
from zope.component import queryUtility
from zope.event import notify
from zope.interface import alsoProvides

import unittest


class RefreshBehaviorTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def _enable_refresh_behavior(self):
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        behaviors = list(fti.behaviors)
        behaviors.append(IRefresh.__identifier__)
        fti.behaviors = tuple(behaviors)
        # invalidate schema cache
        notify(SchemaInvalidatedEvent('collective.cover.content'))

    def _disable_refresh_behavior(self):
        fti = queryUtility(IDexterityFTI, name='collective.cover.content')
        behaviors = list(fti.behaviors)
        behaviors.remove(IRefresh.__identifier__)
        fti.behaviors = tuple(behaviors)
        # invalidate schema cache
        notify(SchemaInvalidatedEvent('collective.cover.content'))

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, ICoverLayer)
        with api.env.adopt_roles(['Manager']):
            self.cover = api.content.create(
                self.portal, 'collective.cover.content', 'c1')

    def test_refresh_registration(self):
        registration = queryUtility(IBehavior, name=IRefresh.__identifier__)
        self.assertIsNotNone(registration)

    def test_refresh_behavior(self):
        view = api.content.get_view(u'view', self.cover, self.request)
        self.assertNotIn('<meta http-equiv="refresh" content="300" />', view())
        self._enable_refresh_behavior()
        self.cover.enable_refresh = True
        self.assertIn('<meta http-equiv="refresh" content="300" />', view())
        self.cover.ttl = 5
        self.assertIn('<meta http-equiv="refresh" content="5" />', view())
        self._disable_refresh_behavior()
        self.assertNotIn('<meta http-equiv="refresh" content="5" />', view())
