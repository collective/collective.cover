# -*- coding: utf-8 -*-
from collective.cover.config import DEFAULT_GRID_SYSTEM
from collective.cover.config import IS_PLONE_5
from collective.cover.controlpanel import ICoverSettings
from collective.cover.testing import INTEGRATION_TESTING
from persistent.mapping import PersistentMapping
from plone import api
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
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

    def _create_cover(self, id, layout):
        with api.env.adopt_roles(['Manager']):
            return api.content.create(
                self.portal, 'collective.cover.content',
                id,
                template_layout=layout,
            )

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
        self.assertGreaterEqual(int(version), int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 2)

    @unittest.skipIf(IS_PLONE_5, 'Upgrade step not supported under Plone 5')
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
        self.assertGreaterEqual(int(version), int(self.to_version))
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
        self.assertGreaterEqual(int(version), int(self.to_version))
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
        self.assertGreaterEqual(int(version), int(self.to_version))
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


class Upgrade9to10TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'9', u'10')

    def test_upgrade_to_10_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertTrue(int(version) >= int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 1)

    def test_new_uuids_structure(self):
        title = u'Upgrade carousel tiles'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        cover = self._create_cover('test-cover', 'Empty layout')
        cover.cover_layout = (
            '[{"type": "row", "children": [{"column-size": 16, "type": '
            '"group", "children": [{"tile-type": '
            '"collective.cover.carousel", "type": "tile", "id": '
            '"ca6ba6675ef145e4a569c5e410af7511"}], "roles": ["Manager"]}]}]'
        )

        tile = cover.get_tile('ca6ba6675ef145e4a569c5e410af7511')
        old_data = ITileDataManager(tile).get()
        old_data['uuids'] = ['uuid1', 'uuid3', 'uuid2']
        ITileDataManager(tile).set(old_data)

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        old_data = ITileDataManager(tile).get()
        self.assertFalse(isinstance(old_data['uuids'], list))
        self.assertTrue(isinstance(old_data['uuids'], dict))
        self.assertEqual(old_data['uuids']['uuid1']['order'], u'0')
        self.assertEqual(old_data['uuids']['uuid2']['order'], u'2')
        self.assertEqual(old_data['uuids']['uuid3']['order'], u'1')


class Upgrade10to11TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'10', u'11')

    def test_upgrade_to_11_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertTrue(int(version) >= int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 6)

    def test_uuids_converted_to_dict(self):
        title = u'Revert PersistentMapping back to dict'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        cover = self._create_cover('test-cover', 'Empty layout')
        cover.cover_layout = (
            '[{"type": "row", "children": [{"column-size": 16, "type": '
            '"group", "children": [{"tile-type": '
            '"collective.cover.carousel", "type": "tile", "id": '
            '"ca6ba6675ef145e4a569c5e410af7511"}], "roles": ["Manager"]}]}]'
        )

        tile = cover.get_tile('ca6ba6675ef145e4a569c5e410af7511')
        old_data = ITileDataManager(tile).get()
        old_dict = PersistentMapping()
        old_dict['uuid1'] = {'order': u'0'}
        old_dict['uuid2'] = {'order': u'1'}
        old_dict['uuid3'] = {'order': u'2'}
        old_data['uuids'] = old_dict
        ITileDataManager(tile).set(old_data)

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        old_data = ITileDataManager(tile).get()
        self.assertFalse(isinstance(old_data['uuids'], PersistentMapping))
        self.assertTrue(isinstance(old_data['uuids'], dict))
        self.assertEqual(old_data['uuids']['uuid1']['order'], u'0')
        self.assertEqual(old_data['uuids']['uuid2']['order'], u'1')
        self.assertEqual(old_data['uuids']['uuid3']['order'], u'2')

    def test_remove_css_class_layout(self):
        title = u'Update layouts'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        old_data = (
            u'[{"type": "row", "class": "row", "children": [{"column-size": 16, '
            u'"type": "group", "children": [{"class": "tile", "tile-type": '
            u'"collective.cover.carousel", '
            u'"type": "tile", "id": "ca6ba6675ef145e4a569c5e410af7511"}], '
            u'"roles": ["Manager"]}]}]'
        )

        expected = (
            u'[{"type": "row", "children": [{"type": "group", "children": '
            u'[{"tile-type": "collective.cover.carousel", "type": "tile", '
            u'"id": "ca6ba6675ef145e4a569c5e410af7511"}], "roles": '
            u'["Manager"], "column-size": 16}]}]'
        )

        # simulate state on previous version of registry layouts
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        settings.layouts = {
            u'test_layout': old_data
        }

        # simulate state on previous version of cover layout
        cover = self._create_cover('test-cover', 'Empty layout')
        cover.cover_layout = old_data

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)

        self.assertEqual(settings.layouts, {'test_layout': expected})
        self.assertEqual(cover.cover_layout, expected)

    def test_remove_orphan_annotations(self):
        from collective.cover.tiles.configuration import ANNOTATIONS_KEY_PREFIX
        from zope.annotation.interfaces import IAnnotations

        title = u'Remove orphan annotations'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        c1 = self._create_cover('c1', 'Layout A')
        annotations = IAnnotations(c1)
        foo = ANNOTATIONS_KEY_PREFIX + '.foo'
        annotations[foo] = 'bar'  # add orphan annotation

        self._create_cover('c2', 'Layout B')  # cover with no annotations

        # simulate state on previous version
        self._do_upgrade_step(step)
        self.assertNotIn(foo, annotations)

    def test_simplify_layout(self):
        title = u'Simplify layouts'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        old_data = (
            u'[{"type": "row", "children": [{"data": {"layout-type": "column", '
            u'"column-size": 16}, "type": "group", "children": [{"tile-type": '
            u'"collective.cover.carousel", "type": "tile", "id": '
            u'"ca6ba6675ef145e4a569c5e410af7511"}], "roles": ["Manager"]}]}]'
        )

        expected = (
            u'[{"type": "row", "children": [{"type": "group", "children": '
            u'[{"tile-type": "collective.cover.carousel", "type": "tile", '
            u'"id": "ca6ba6675ef145e4a569c5e410af7511"}], "roles": '
            u'["Manager"], "column-size": 16}]}]'
        )

        # simulate state on previous version of registry layouts
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        settings.layouts = {
            u'test_layout': old_data
        }

        # simulate state on previous version of cover layout
        cover = self._create_cover('test-cover', 'Empty layout')
        cover.cover_layout = old_data

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)

        self.assertEqual(settings.layouts, {'test_layout': expected})
        self.assertEqual(cover.cover_layout, expected)


class Upgrade11to12TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'11', u'12')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertTrue(int(version) >= int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 1)

    def test_update_role_map(self):
        # address also an issue with Setup permission
        title = u'Add Embed Code permission'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        self.portal._collective_cover__Embed_Code_Permission = ()
        self.portal._collective_cover__Setup_Permission = ()

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        permissions = ['collective.cover: Setup', 'collective.cover: Embed Code']
        expected = ['Manager', 'Site Administrator']
        for p in permissions:
            roles = self.portal.rolesOfPermission(p)
            roles = [r['name'] for r in roles if r['selected']]
            self.assertListEqual(roles, expected)


class Upgrade12to13TestCase(UpgradeTestCaseBase):

    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u'12', u'13')

    def test_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertTrue(int(version) >= int(self.to_version))
        self.assertEqual(self._how_many_upgrades_to_do(), 4)

    @unittest.skipIf(IS_PLONE_5, 'Upgrade step not supported under Plone 5')
    def test_fix_resources_references(self):
        # address also an issue with Setup permission
        title = u'Fix resource references'
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        from collective.cover.upgrades.v13 import _rename_resources
        from collective.cover.upgrades.v13 import RESOURCES_TO_FIX
        RESOURCES_TO_FIX_INVERSE = {v: k for k, v in RESOURCES_TO_FIX.items()}

        css_tool = api.portal.get_tool('portal_css')
        _rename_resources(css_tool, RESOURCES_TO_FIX_INVERSE)

        js_tool = api.portal.get_tool('portal_javascripts')
        _rename_resources(js_tool, RESOURCES_TO_FIX_INVERSE)

        css_ids = css_tool.getResourceIds()
        self.assertIn('++resource++collective.cover/contentchooser.css', css_ids)
        self.assertIn('++resource++collective.cover/cover.css', css_ids)
        self.assertNotIn('++resource++collective.cover/css/contentchooser.css', css_ids)
        self.assertNotIn('++resource++collective.cover/css/cover.css', css_ids)

        js_ids = js_tool.getResourceIds()
        self.assertIn('++resource++collective.cover/contentchooser.js', js_ids)
        self.assertIn('++resource++collective.cover/jquery.endless-scroll.js', js_ids)
        self.assertNotIn('++resource++collective.cover/js/contentchooser.js', js_ids)
        self.assertNotIn('++resource++collective.cover/js/vendor/jquery.endless-scroll.js', js_ids)

        for res in RESOURCES_TO_FIX:
            ids = css_ids
            if res.endswith('js'):
                ids = js_ids
            self.assertIn(res, ids)
            self.assertNotIn(RESOURCES_TO_FIX[res], ids)

        cptool = api.portal.get_tool('portal_controlpanel')
        configlet = cptool.getActionObject('Products/cover')
        configlet.setIconExpression('string:${portal_url}/++resource++collective.cover/frontpage_icon.png')

        types = api.portal.get_tool('portal_types')
        cover_type = types['collective.cover.content']
        cover_type.icon_expr = 'string:${portal_url}/++resource++collective.cover/frontpage_icon.png'

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)

        css_ids = css_tool.getResourceIds()
        self.assertIn('++resource++collective.cover/css/contentchooser.css', css_ids)
        self.assertIn('++resource++collective.cover/css/cover.css', css_ids)
        self.assertNotIn('++resource++collective.cover/contentchooser.css', css_ids)
        self.assertNotIn('++resource++collective.cover/cover.css', css_ids)

        js_ids = js_tool.getResourceIds()
        self.assertIn('++resource++collective.cover/js/contentchooser.js', js_ids)
        self.assertIn('++resource++collective.cover/js/vendor/jquery.endless-scroll.js', js_ids)
        self.assertNotIn('++resource++collective.cover/contentchooser.js', js_ids)
        self.assertNotIn('++resource++collective.cover/jquery.endless-scroll.js', js_ids)

        configlet = cptool.getActionObject('Products/cover')
        self.assertEqual(
            configlet.getIconExpression(),
            'string:${portal_url}/++resource++collective.cover/img/frontpage_icon.png')

        self.assertEqual(
            cover_type.icon_expr,
            'string:${portal_url}/++resource++collective.cover/img/frontpage_icon.png')


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
        assert step is not None

        # simulate state on previous version
        tile = u'collective.cover.calendar'

        record = dict(name='plone.app.tiles')
        registered_tiles = api.portal.get_registry_record(**record)
        registered_tiles.remove(tile)
        api.portal.set_registry_record(value=registered_tiles, **record)
        registered_tiles = api.portal.get_registry_record(**record)
        assert tile not in registered_tiles

        record = dict(interface=ICoverSettings, name='available_tiles')
        available_tiles = api.portal.get_registry_record(**record)
        available_tiles.remove(tile)
        api.portal.set_registry_record(value=available_tiles, **record)
        available_tiles = api.portal.get_registry_record(**record)
        assert tile not in available_tiles

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
        assert step is not None

        # simulate state on previous version
        js_tool = api.portal.get_tool('portal_javascripts')
        js_tool.unregisterResource('++resource++collective.cover/js/main.js')

        script = '++resource++collective.cover/js/main.js'
        assert script not in js_tool.getResourceIds()

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
        assert step is not None

        # simulate state on previous version
        cover = self._create_cover('test-cover', 'Empty layout')
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
        assert isinstance(data['image_mtime'], str)

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
