# -*- coding: utf-8 -*-

from collective.cover.config import DEFAULT_GRID_SYSTEM
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


class UpgradeTestCaseBase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self, from_version, to_version):
        self.portal = self.layer['portal']
        self.setup = self.portal['portal_setup']
        self.profile_id = u'collective.cover:default'
        self.from_version = from_version
        self.to_version = to_version

    def _get_upgrade_step(self, title):
        """Get one of the upgrade steps.

        Keyword arguments:
        title -- the title used to register the upgrade step
        """
        self.setup.setLastVersionForProfile(self.profile_id, self.from_version)
        upgrades = self.setup.listUpgrades(self.profile_id)
        steps = [s for s in upgrades[0] if s['title'] == title]
        return steps[0] if steps else None

    def _do_upgrade_step(self, step):
        """Execute an upgrade step.

        Keyword arguments:
        step -- the step we want to run
        """
        request = self.layer['request']
        request.form['profile_id'] = self.profile_id
        request.form['upgrades'] = [step['id']]
        self.setup.manage_doUpgrades(request=request)

    def _how_many_upgrades_to_do(self):
        self.setup.setLastVersionForProfile(self.profile_id, self.from_version)
        upgrades = self.setup.listUpgrades(self.profile_id)
        assert len(upgrades) > 0
        return len(upgrades[0])


class Upgrade5to6TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'5', u'6')

    def test_upgrade_to_6_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertTrue(version >= self.to_version)
        self.assertEqual(self._how_many_upgrades_to_do(), 2)

    def test_issue_201(self):
        # check if the upgrade step is registered
        title = u'issue 201'
        description = u'Depend on collective.js.bootstrap.'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)

        css_tool = self.portal['portal_css']
        js_tool = self.portal['portal_javascripts']
        old_css = '++resource++collective.cover/bootstrap.min.css'
        old_js = '++resource++collective.cover/bootstrap.min.js'
        new_js = '++resource++collective.js.bootstrap/js/bootstrap.min.js'

        # simulate state on previous version
        css_tool.registerResource(old_css)
        js_tool.renameResource(new_js, old_js)
        self.assertIn(old_css, css_tool.getResourceIds())
        self.assertIn(old_js, js_tool.getResourceIds())
        self.assertNotIn(new_js, js_tool.getResourceIds())

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)

        self.assertNotIn(old_css, css_tool.getResourceIds())
        self.assertNotIn(old_js, js_tool.getResourceIds())
        self.assertIn(new_js, js_tool.getResourceIds())

    def test_issue_303(self):
        # check if the upgrade step is registered
        title = u'issue 303'
        description = u'Remove unused bundles from portal_javascript.'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)

        js_tool = self.portal['portal_javascripts']

        # simulate state on previous version
        JQ_JS_IDS = ['++resource++plone.app.jquerytools.js',
                     '++resource++plone.app.jquerytools.form.js',
                     '++resource++plone.app.jquerytools.overlayhelpers.js',
                     '++resource++plone.app.jquerytools.plugins.js',
                     '++resource++plone.app.jquerytools.dateinput.js',
                     '++resource++plone.app.jquerytools.rangeinput.js',
                     '++resource++plone.app.jquerytools.validator.js']
        TINYMCE_JS_IDS = ['tiny_mce.js', 'tiny_mce_init.js']

        for id in js_tool.getResourceIds():
            js = js_tool.getResource(id)
            if id in JQ_JS_IDS:
                js.setBundle('jquerytools')
            elif id in TINYMCE_JS_IDS:
                js.setBundle('tinymce')

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)

        for id in js_tool.getResourceIds():
            if id in JQ_JS_IDS or id in TINYMCE_JS_IDS:
                js = js_tool.getResource(id)
                self.assertEqual('default', js.getBundle())


class Upgrade6to7TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'6', u'7')

    def test_upgrade_to_7_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertTrue(version >= self.to_version)
        self.assertEqual(self._how_many_upgrades_to_do(), 3)

    def test_issue_330(self):
        # check if the upgrade step is registered
        title = u'issue 330'
        description = u'Add grid_system field to registry'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)
        record_name = \
            'collective.cover.controlpanel.ICoverSettings.grid_system'

        # simulate state on previous version
        registry = getUtility(IRegistry)
        del registry.records[record_name]

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        self.assertEqual(registry.records[record_name].value,
                         DEFAULT_GRID_SYSTEM)

    def test_layout_edit_permission(self):
        # check if the upgrade step is registered
        title = u'New permission for Layout edit tab'
        description = (u'Protect Layout edit tab with new permission '
                       u'granted to Managers and Site Admins')

        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)

        # simulate state on previous version
        types = api.portal.get_tool('portal_types')
        cover_type = types['collective.cover.content']
        action = cover_type.getActionObject('object/layoutedit')
        action.permissions = (u'Modify portal content', )

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        action = cover_type.getActionObject('object/layoutedit')
        self.assertEqual(action.permissions,
                         (u'collective.cover: Can Edit Layout', ))


class Upgrade7to8TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'7', u'8')

    def test_upgrade_to_8_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertTrue(version >= self.to_version)
        self.assertEqual(self._how_many_upgrades_to_do(), 1)

    def test_issue_371(self):
        title = u'issue_371'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)


class Upgrade8to9TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'8', u'9')

    def test_upgrade_to_9_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertTrue(version >= self.to_version)
        self.assertEqual(self._how_many_upgrades_to_do(), 3)

    def test_issue_423(self):
        title = u'issue_423'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        cptool = api.portal.get_tool('portal_controlpanel')
        configlet = cptool.getActionObject('Products/cover')
        configlet.permissions = ('cmf.ManagePortal',)

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        permissions = configlet.permissions
        self.assertEqual(permissions, ('collective.cover: Setup',))
