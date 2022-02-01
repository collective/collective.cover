# -*- coding: utf-8 -*-
from collective.cover.config import PROJECTNAME
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.browserlayer.utils import registered_layers
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.utils import get_installer
from zope.component import getUtility

import unittest


JS = "++resource++collective.js.bootstrap/js/bootstrap.min.js"


class InstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.registry = getUtility(IRegistry)
        self.installer = get_installer(self.portal, self.request)

    def test_installed(self):
        self.assertTrue(self.installer.is_product_installed(PROJECTNAME))

    def test_addon_layer(self):
        layers = [layer.getName() for layer in registered_layers()]
        self.assertIn("ICoverLayer", layers)

    def test_resources_available(self):
        res = self.portal.restrictedTraverse(JS)
        self.assertTrue(res)

    def test_jsregistry(self):
        bundles = self.registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles"
        )
        bundle = bundles["bootstrap"]

        self.assertEqual(bundle.jscompilation, JS)

    def test_reinstall_with_changed_registry(self):
        ps = getattr(self.portal, "portal_setup")
        try:
            ps.runAllImportStepsFromProfile("profile-collective.cover:default")
        except AttributeError:
            self.fail("Reinstall fails when the record was changed")

    def test_versioning_policy(self):
        repository = self.portal["portal_repository"]
        policy_map = repository.getPolicyMap()["collective.cover.content"]
        self.assertEqual(policy_map, [u"version_on_revert"])


class UninstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.registry = getUtility(IRegistry)
        self.installer = get_installer(self.portal, self.request)

        with api.env.adopt_roles(["Manager"]):
            self.installer.uninstall_product(PROJECTNAME)

    def test_uninstalled(self):
        self.assertFalse(self.installer.is_product_installed(PROJECTNAME))

    def test_addon_layer_removed(self):
        layers = [layer.getName() for layer in registered_layers()]
        self.assertNotIn("ICoverLayer", layers)

    def test_jsregistry_removed(self):
        bundles = self.registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles"
        )

        self.assertNotIn("bootstrap", bundles.keys())

    @unittest.expectedFailure  # XXX: not pretty sure how to test this
    def test_versioning_policy_removed(self):
        repository = self.portal["portal_repository"]
        policy_map = repository.getPolicyMap()
        self.assertNotIn("collective.cover.content", policy_map)
