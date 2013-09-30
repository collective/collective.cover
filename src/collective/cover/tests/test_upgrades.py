# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.upgrades import register_available_tiles_record
from collective.cover.upgrades import register_styles_record
from collective.cover.upgrades import rename_content_chooser_resources
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRecordAddedEvent
from plone.registry.interfaces import IRegistry
from zope.component import eventtesting
from zope.component import getUtility

import unittest


class Upgrade2to3TestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_rename_content_chooser_resources(self):
        # writing a real test for this will need a mock tool for
        # ResourceRegistries and I don't think it worths the time, so just
        # call the function and check it runs with no errors
        css_tool = self.portal['portal_css']
        js_tool = self.portal['portal_javascripts']
        rename_content_chooser_resources(self.portal)
        self.assertNotIn(
            '++resource++collective.cover/screenlets.css',
            css_tool.getResourceIds()
        )
        self.assertNotIn(
            '++resource++collective.cover/screenlets.js',
            js_tool.getResourceIds()
        )
        self.assertIn(
            '++resource++collective.cover/contentchooser.css',
            css_tool.getResourceIds()
        )
        self.assertIn(
            '++resource++collective.cover/contentchooser.js',
            js_tool.getResourceIds()
        )

    def test_register_available_tiles_record(self):
        registry = getUtility(IRegistry)
        record = 'collective.cover.controlpanel.ICoverSettings.available_tiles'

        eventtesting.setUp()

        # calling the handler here should have no effect as we are running the
        # latest profile version
        eventtesting.clearEvents()
        register_available_tiles_record(self.portal)
        events = eventtesting.getEvents(IRecordAddedEvent)
        self.assertEqual(len(events), 0)

        # now we delete the record and rerun the handler to verify the record
        # was added
        del registry.records[record]
        eventtesting.clearEvents()
        register_available_tiles_record(self.portal)
        events = eventtesting.getEvents(IRecordAddedEvent)
        self.assertNotEqual(len(events), 0)
        self.assertIn(record, registry.records)
        eventtesting.clearEvents()


class Upgrade3to4TestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_register_styles_record(self):
        registry = getUtility(IRegistry)
        record = 'collective.cover.controlpanel.ICoverSettings.styles'

        eventtesting.setUp()

        # just delete the existing record and rerun the handler to verify it
        # was added again
        del registry.records[record]
        eventtesting.clearEvents()
        register_styles_record(self.portal)
        events = eventtesting.getEvents(IRecordAddedEvent)
        self.assertNotEqual(len(events), 0)
        self.assertIn(record, registry.records)
        eventtesting.clearEvents()

    def test_issue_218(self):
        from collective.cover.upgrades import issue_218
        registry = getUtility(IRegistry)
        record = 'plone.app.tiles'

        # we set the record to contain only the tiles we care
        registry[record] = [
            u'collective.cover.image',
            u'collective.cover.link',
        ]

        # this upgrade step must remve the above tiles and
        # add the new banner tile
        issue_218(self.portal)
        self.assertIn(u'collective.cover.banner', registry[record])
        self.assertNotIn(u'collective.cover.image', registry[record])
        self.assertNotIn(u'collective.cover.link', registry[record])


class Upgrade4to5TestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup = self.portal['portal_setup']
        self.profile_id = u'collective.cover:default'
        self.tinymce = self.portal.portal_tinymce
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory(
            'collective.cover.content', 'cover', template_layout='Layout B')
        self.cover = self.folder['cover']
        self.layout_view = self.cover.restrictedTraverse('layout')

    def test_upgrade_to_5_registrations(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)
        self.assertEqual(version, (u'5',))
        self.setup.setLastVersionForProfile(self.profile_id, u'4')
        upgrades = self.setup.listUpgrades(self.profile_id)
        self.assertEqual(len(upgrades), 1)
        self.assertEqual(len(upgrades[0]), 6)

    def _get_upgrade_step(self, title):
        """Get one of the upgrade steps from 4 to 5.

        Keyword arguments:
        title -- the title used to register the upgrade step
        """
        self.setup.setLastVersionForProfile(self.profile_id, u'4')
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

    def test_issue_244(self):
        # check if the upgrade step is registered
        title = u'issue_244'
        description = u"Add cover.css to css_registry."
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)

        css_tool = self.portal['portal_css']
        id = '++resource++collective.cover/cover.css'

        # remove the resource so simulate status of profile version 4
        css_tool.unregisterResource(id)
        self.assertNotIn(id, css_tool.getResourceIds())

        # and now run the upgrade step to validate the update
        self._do_upgrade_step(step)
        self.assertIn(id, css_tool.getResourceIds())

    def test_issue_262(self):
        # check if the upgrade step is registered
        title = u'issue_262'
        description = u"Default value for css_class."
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)

        # get tiles and assign css_class as before version 5
        layout = self.layout_view.get_layout('view')
        tile_def = layout[0]['children'][0]['children'][0]
        self.tile1 = self.cover.restrictedTraverse('{0}/{1}'.format(tile_def['tile-type'], tile_def['id']))
        tile_config = self.tile1.get_tile_configuration()
        tile_config['css_class'] = {'order': u'0', 'visibility': u'on'}
        self.tile1.set_tile_configuration(tile_config)

        tile_def = layout[0]['children'][1]['children'][0]
        self.tile2 = self.cover.restrictedTraverse('{0}/{1}'.format(tile_def['tile-type'], tile_def['id']))
        tile_config = self.tile2.get_tile_configuration()
        tile_config['css_class'] = u"--NOVALUE--"
        self.tile2.set_tile_configuration(tile_config)

        tile_def = layout[1]['children'][0]['children'][0]
        self.tile3 = self.cover.restrictedTraverse('{0}/{1}'.format(tile_def['tile-type'], tile_def['id']))
        tile_config = self.tile3.get_tile_configuration()
        tile_config['css_class'] = u""
        self.tile3.set_tile_configuration(tile_config)

        tile_def = layout[1]['children'][1]['children'][0]
        self.tile4 = self.cover.restrictedTraverse('{0}/{1}'.format(tile_def['tile-type'], tile_def['id']))
        tile_config = self.tile4.get_tile_configuration()
        tile_config['css_class'] = u"tile-shadow"
        self.tile4.set_tile_configuration(tile_config)

        registry = getUtility(IRegistry)
        record = 'collective.cover.controlpanel.ICoverSettings.styles'
        default_style = u"-Default-|tile-default"

        # FIXME: this must be tested outside the upgrade step also
        # default installation includes the '-Default-|tile-default' style
        self.assertIn(default_style, registry[record])

        # simulate version 4 state by removing default style
        register_styles_record(self.portal)
        self.assertNotIn(default_style, registry[record])

        # after upgrade step, old tiles have a new default value for
        # css_class field (if they didn't have one)
        self._do_upgrade_step(step)

        # upgraded installations include default style
        self.assertIn(default_style, registry[record])

        self.assertEqual(
            self.tile1.get_tile_configuration()['css_class'], u"tile-default")
        self.assertEqual(
            self.tile2.get_tile_configuration()['css_class'], u"tile-default")
        self.assertEqual(
            self.tile3.get_tile_configuration()['css_class'], u"tile-default")
        self.assertEqual(
            self.tile4.get_tile_configuration()['css_class'], u"tile-shadow")

    def test_issue_259(self):
        # check if the upgrade step is registered
        title = u'issue_259'
        description = u"Make cover linkable from TinyMCE."
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)

        # default installation includes Cover as linkable
        linkables = self.tinymce.linkable.split('\n')
        self.assertIn(u'collective.cover.content', linkables)

        # remove cover from linkables to simulate version 4
        linkables.remove(u'collective.cover.content')
        self.tinymce.linkable = '\n'.join(linkables)
        linkables = self.tinymce.linkable.split('\n')
        self.assertNotIn(u'collective.cover.content', linkables)

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        linkables = self.tinymce.linkable.split('\n')
        self.assertIn(u'collective.cover.content', linkables)

    def test_issue_35(self):
        # check if the upgrade step is registered
        title = u'issue_35'
        description = u"Link integrity on Rich Text tile references."
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)

        # remove behavior to simulate version 4 state
        fti = getUtility(IDexterityFTI, name='collective.cover.content')
        referenceable = u'plone.app.referenceablebehavior.referenceable.IReferenceable'
        behaviors = list(fti.behaviors)
        behaviors.remove(referenceable)
        fti.behaviors = tuple(behaviors)
        fti = getUtility(IDexterityFTI, name='collective.cover.content')
        self.assertNotIn(referenceable, fti.behaviors)

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        fti = getUtility(IDexterityFTI, name='collective.cover.content')
        self.assertIn(referenceable, fti.behaviors)

    def test_issue_271(self):
        # check if the upgrade step is registered
        title = u'issue_271'
        description = u"Implement standard content type view."
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)

        # default installation includes alternate view
        portal_types = self.portal['portal_types']
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertIn(u'standard', view_methods)

        # remove alternate view to simulate version 4 state
        portal_types['collective.cover.content'].view_methods = ('view',)
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertNotIn(u'standard', view_methods)

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertIn(u'standard', view_methods)

    def test_issue_294(self):
        # check if the upgrade step is registered
        title = u'issue_294'
        description = u"Install IRelatedItems behavior."
        step = self._get_upgrade_step(title)
        self.assertIsNotNone(step)
        self.assertEqual(step['description'], description)

        # remove behavior to simulate version 4 state
        fti = getUtility(IDexterityFTI, name='collective.cover.content')
        related_items = u'plone.app.relationfield.behavior.IRelatedItems'
        behaviors = list(fti.behaviors)
        behaviors.remove(related_items)
        fti.behaviors = tuple(behaviors)
        fti = getUtility(IDexterityFTI, name='collective.cover.content')
        self.assertNotIn(related_items, fti.behaviors)

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        fti = getUtility(IDexterityFTI, name='collective.cover.content')
        self.assertIn(related_items, fti.behaviors)
