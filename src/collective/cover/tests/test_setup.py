# -*- coding: utf-8 -*-
from collective.cover.config import IS_PLONE_5
from collective.cover.config import PROJECTNAME
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.browserlayer.utils import registered_layers

import unittest


JS = [
    '++resource++collective.js.bootstrap/js/bootstrap.min.js',
]


class InstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']

    def test_installed(self):
        self.assertTrue(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('ICoverLayer', layers)

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
    def test_jsregistry(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id_ in JS:
            self.assertIn(id_, resource_ids, '{0} not installed'.format(id))

    def test_resources_available(self):
        resources = JS
        for id_ in resources:
            res = self.portal.restrictedTraverse(id_)
            self.assertTrue(res)

    def test_reinstall_with_changed_registry(self):
        ps = getattr(self.portal, 'portal_setup')
        try:
            ps.runAllImportStepsFromProfile('profile-collective.cover:default')
        except AttributeError:
            self.fail('Reinstall fails when the record was changed')

    def test_versioning_policy(self):
        repository = self.portal['portal_repository']
        policy_map = repository.getPolicyMap()['collective.cover.content']
        self.assertEqual(policy_map, [u'version_on_revert'])

    @unittest.skipIf(IS_PLONE_5, 'Plone 4.3 only')
    def test_tinymce_linkable(self):
        tinymce = self.portal['portal_tinymce']
        linkable = tinymce.linkable.split('\n')
        self.assertIn('collective.cover.content', linkable)


class UninstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('ICoverLayer', layers)

    @unittest.skipIf(IS_PLONE_5, 'No easy way to test this under Plone 5')
    def test_jsregistry_removed(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id_ in JS:
            self.assertNotIn(id_, resource_ids, '{0} not removed'.format(id))

    @unittest.expectedFailure  # XXX: not pretty sure how to test this
    def test_versioning_policy_removed(self):
        repository = self.portal['portal_repository']
        policy_map = repository.getPolicyMap()
        self.assertNotIn('collective.cover.content', policy_map)

    @unittest.skipIf(IS_PLONE_5, 'Plone 4.3 only')
    def test_tinymce_linkable_removed(self):
        tinymce = self.portal['portal_tinymce']
        linkable = tinymce.linkable.split('\n')
        self.assertNotIn('collective.cover.content', linkable)
