# -*- coding: utf-8 -*-

from collective.cover.testing import INTEGRATION_TESTING
from collective.cover.upgrades import register_available_tiles_record
from collective.cover.upgrades import register_styles_record
from collective.cover.upgrades import rename_content_chooser_resources
from collective.cover.upgrades import issue_244
from collective.cover.upgrades import update_styles_record_4_5
from collective.cover.upgrades import set_new_default_class_4_5
from collective.cover.upgrades import tinymce_linkable
from collective.cover.upgrades import register_alternate_view
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
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
        self.tinymce = self.portal.portal_tinymce
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('collective.cover.content', 'cover',
                                  template_layout='Layout B')
        self.cover = self.folder['cover']
        self.layout_view = self.cover.restrictedTraverse('layout')

    def test_issue_244(self):
        css_tool = self.portal['portal_css']
        id = '++resource++collective.cover/cover.css'
        # remove the resource so simulate status of profile version 4
        css_tool.unregisterResource(id)
        self.assertNotIn(id, css_tool.getResourceIds())
        issue_244(self.portal)
        self.assertIn(id, css_tool.getResourceIds())

    def test_issue_262(self):
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

        # default installation includes the '-Default-|tile-default' style
        self.assertIn(default_style, registry[record])

        # old installations (upgraded up to version 4) didn't include default style
        register_styles_record(self.portal)
        self.assertNotIn(default_style, registry[record])

        # upgraded installations (up to version 5) include default style
        update_styles_record_4_5(self.portal)
        self.assertIn(default_style, registry[record])

        # after upgrade step, old tiles have a new default value for
        # css_class field (if they didn't have one)
        set_new_default_class_4_5(self.portal)
        self.assertEqual(self.tile1.get_tile_configuration()['css_class'], u"tile-default")
        self.assertEqual(self.tile2.get_tile_configuration()['css_class'], u"tile-default")
        self.assertEqual(self.tile3.get_tile_configuration()['css_class'], u"tile-default")
        self.assertEqual(self.tile4.get_tile_configuration()['css_class'], u"tile-shadow")

    def test_tinymce_linkables(self):
        # default installation includes Cover as linkable
        linkables = self.tinymce.linkable.split('\n')
        self.assertIn(u'collective.cover.content', linkables)

        # remove cover from linkables to simulate version 4
        linkables.remove(u'collective.cover.content')
        self.tinymce.linkable = '\n'.join(linkables)
        linkables = self.tinymce.linkable.split('\n')
        self.assertNotIn(u'collective.cover.content', linkables)

        # and now run the upgrade step to check that worked
        tinymce_linkable(self.portal)
        linkables = self.tinymce.linkable.split('\n')
        self.assertIn(u'collective.cover.content', linkables)

    def test_register_alternate_view(self):
        # default installation includes alternate view
        portal_types = self.portal['portal_types']
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertIn(u'alternate', view_methods)

        # remove alternate view to simulate version 4 state
        portal_types['collective.cover.content'].view_methods = ('view',)
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertNotIn(u'alternate', view_methods)

        # and now run the upgrade step to validate the update
        register_alternate_view(self.portal)
        view_methods = portal_types['collective.cover.content'].view_methods
        self.assertIn(u'alternate', view_methods)
