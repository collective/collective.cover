# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getMultiAdapter
from zope.component import getUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry

from collective.cover.config import DEFAULT_SEARCHABLE_CONTENT_TYPES
from collective.cover.config import PROJECTNAME
from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import INTEGRATION_TESTING


class ControlPanelTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.controlpanel = self.portal['portal_controlpanel']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_controlpanel_has_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name='cover-settings')
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@cover-settings')

    def test_controlpanel_installed(self):
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertTrue('cover' in actions,
                        'control panel was not installed')

    def test_controlpanel_removed_on_uninstall(self):
        qi = self.portal['portal_quickinstaller']
        qi.uninstallProducts(products=[PROJECTNAME])
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertTrue('cover' not in actions,
                        'control panel was not removed')


class RegistryTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(ICoverSettings)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_sections_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'layouts'))
        self.assertNotEqual(self.settings.layouts, None)

    def test_searchable_content_types_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'searchable_content_types'))
        self.assertListEqual(self.settings.searchable_content_types,
                             DEFAULT_SEARCHABLE_CONTENT_TYPES)

    def get_record(self, record):
        """ Helper function; it raises KeyError if the record is not in the
        registry.
        """
        prefix = 'collective.cover.controlpanel.ICoverSettings.'
        return self.registry[prefix + record]

    def test_records_removed_on_uninstall(self):
        # XXX: I haven't found a better way to test this; anyone?
        qi = self.portal['portal_quickinstaller']
        qi.uninstallProducts(products=[PROJECTNAME])
        self.assertRaises(KeyError, self.get_record, 'layouts')
        self.assertRaises(KeyError, self.get_record, 'searchable_content_types')
