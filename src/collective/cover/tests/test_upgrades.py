# -*- coding: utf-8 -*-
from collective.cover.config import IS_PLONE_5
from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import INTEGRATION_TESTING
from plone import api
from plone.tiles.interfaces import ITileDataManager

import unittest


class UpgradeTestCaseBase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self, from_version, to_version):
        self.portal = self.layer['portal']
        self.setup = self.portal['portal_setup']
        self.profile_id = u'collective.cover:default'
        self.from_version = from_version
        self.to_version = to_version

    def _create_cover(self, **kwargs):
        with api.env.adopt_roles(['Manager']):
            return api.content.create(
                self.portal, 'collective.cover.content', **kwargs)

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
        return len(upgrades[0])


class Upgrade13to14TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'13', u'14')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 4)

    # FIXME: https://github.com/collective/collective.cover/issues/633
    @unittest.skipIf(IS_PLONE_5, 'Upgrade step not supported under Plone 5')
    def test_register_calendar_tile(self):
        # address also an issue with Setup permission
        title = u'Register calendar tile'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        tile = u'collective.cover.calendar'

        record = dict(name='plone.app.tiles')
        registered_tiles = api.portal.get_registry_record(**record)
        registered_tiles.remove(tile)
        api.portal.set_registry_record(value=registered_tiles, **record)
        registered_tiles = api.portal.get_registry_record(**record)
        self.assertNotIn(tile, registered_tiles)

        record = dict(interface=ICoverSettings, name='available_tiles')
        available_tiles = api.portal.get_registry_record(**record)
        available_tiles.remove(tile)
        api.portal.set_registry_record(value=available_tiles, **record)
        available_tiles = api.portal.get_registry_record(**record)
        self.assertNotIn(tile, available_tiles)

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)

        registered_tiles = api.portal.get_registry_record(
            name='plone.app.tiles')
        self.assertIn(tile, registered_tiles)

        available_tiles = api.portal.get_registry_record(
            interface=ICoverSettings, name='available_tiles')
        self.assertIn(tile, available_tiles)

    def test_register_calendar_script(self):
        # address also an issue with Setup permission
        title = u'Register calendar script'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        js_tool = api.portal.get_tool('portal_javascripts')
        js_tool.unregisterResource('++resource++collective.cover/js/main.js')

        script = '++resource++collective.cover/js/main.js'
        self.assertNotIn(script, js_tool.getResourceIds())

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)

        self.assertIn(script, js_tool.getResourceIds())


class Upgrade14to15TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'14', u'15')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 2)

    def test_fix_image_field_modification_time(self):
        from persistent.dict import PersistentDict
        title = u'Fix image field modification time'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        cover = self._create_cover(id='test-cover', layout='Empty layout')
        cover.cover_layout = (
            '[{"type": "row", "children": [{"column-size": 16, "type": '
            '"group", "children": [{"tile-type": '
            '"collective.cover.basic", "type": "tile", "id": '
            '"ca6ba6675ef145e4a569c5e410af7511"}], "roles": ["Manager"]}]}]'
        )

        tile = cover.get_tile('ca6ba6675ef145e4a569c5e410af7511')
        obj = self.portal['my-image']
        tile.populate_with_object(obj)

        dmgr = ITileDataManager(tile)
        old_data = dmgr.get()
        old_data['image_mtime'] = repr(old_data['image_mtime'])
        dmgr.annotations[dmgr.key] = PersistentDict(old_data)

        data = dmgr.get()
        self.assertIsInstance(data['image_mtime'], str)

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)

        data = dmgr.get()
        self.assertIsInstance(data['image_mtime'], float)


class Upgrade15to16TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'15', u'16')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 1)


class Upgrade16to17TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'16', u'17')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 1)


class Upgrade17to18TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'17', u'18')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 2)


class Upgrade18to19TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'18', u'19')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 3)

    def test_purge_deleted_tiles(self):
        from zope.annotation import IAnnotations
        title = u'Purge Deleted Tiles'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        cover = self._create_cover(id='test-cover', layout='Empty layout')

        annotations = IAnnotations(cover)
        key = u'plone.tiles.data.abc123'
        annotations[key] = u'Plone'
        self.assertEqual(annotations[key], u'Plone')

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        self.assertNotIn(key, annotations)

    @unittest.skipIf(IS_PLONE_5, 'Upgrade step not supported under Plone 5')
    def test_register_resource(self):
        # address also an issue with Setup permission
        title = u'Register resource'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        from collective.cover.upgrades.v19 import JS
        js_tool = api.portal.get_tool('portal_javascripts')
        js_tool.unregisterResource(JS)
        self.assertNotIn(JS, js_tool.getResourceIds())

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        self.assertIn(JS, js_tool.getResourceIds())


class Upgrade19to20TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'19', u'20')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 1)


class Upgrade20to21TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'20', u'21')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 1)


class Upgrade21to22TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'21', u'22')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 1)


class Upgrade22to23TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'22', u'23')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 1)

    @staticmethod
    def _set_remote_url_field(tile, remote_url):
        data_mgr = ITileDataManager(tile)
        data = data_mgr.get()
        data.update(remote_url=remote_url)
        data_mgr.set(data)

    def test_add_remote_url_field(self):
        title = u'Show remote_url field on Basic tiles'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        layout = (
            '[{"type": "row", "children": [{"column-size": 12, "type": '
            '"group", "children": [{"tile-type": '
            '"collective.cover.basic", "type": "tile", "id": '
            '"test"}], "roles": ["Manager"]}]}]'
        )
        obj1 = self._create_cover(id='foo', layout='Empty layout')
        obj2 = self._create_cover(id='bar', layout='Empty layout')
        obj1.cover_layout = obj2.cover_layout = layout

        with api.env.adopt_roles(['Manager']):
            news = api.content.create(
                self.portal, 'News Item', title=u'Baz')

        tile = obj1.restrictedTraverse('@@collective.cover.basic/test')
        tile.populate_with_object(news)
        self._set_remote_url_field(tile, None)
        tile = obj1.restrictedTraverse('@@collective.cover.basic/test')
        self.assertIsNone(tile.data['remote_url'])

        tile = obj2.restrictedTraverse('@@collective.cover.basic/test')
        tile.populate_with_object(news)
        remote_url = 'http://example.org/'
        self._set_remote_url_field(tile, remote_url)
        tile = obj2.restrictedTraverse('@@collective.cover.basic/test')
        self.assertEqual(tile.data['remote_url'], remote_url)

        # run the upgrade step to validate the update
        from logging import INFO
        from testfixtures import LogCapture
        config = {'level': INFO, 'attributes': ['getMessage']}
        with LogCapture('collective.cover', **config) as log:
            self._do_upgrade_step(step)

        log.check_present(
            'Found 2 objects in the catalog',
            '/plone/bar ("test"): remote_url=http://example.org/',
        )


class Upgrade23to24TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'23', u'24')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 3)

    def test_deprecate_resource_registries(self):
        title = u'Deprecate resource registries'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        from collective.cover.upgrades.v24 import JS
        from collective.cover.upgrades.v24 import CSS

        js_tool = api.portal.get_tool('portal_javascripts')
        for js in JS:
            js_tool.registerResource(id=js)
            self.assertIn(js, js_tool.getResourceIds())

        css_tool = api.portal.get_tool('portal_css')
        for css in CSS:
            css_tool.registerResource(id=css)
            self.assertIn(css, css_tool.getResourceIds())

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        for js in JS:
            self.assertNotIn(js, js_tool.getResourceIds())
        for css in CSS:
            self.assertNotIn(css, css_tool.getResourceIds())
