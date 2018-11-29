# -*- coding: utf-8 -*-
from collective.cover.testing import INTEGRATION_TESTING
from lxml import etree  # nosec
from plone import api
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewletManager

import unittest


class ResourcesViewletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        with api.env.adopt_roles(['Manager']):
            self.cover = api.content.create(
                self.portal, 'collective.cover.content', 'c1')

        self.viewlet = self.get_viewlet(self.cover)

    def get_viewlet_manager(self, context, name='plone.htmlhead'):
        request = self.request
        view = BrowserView(context, request)
        manager = getMultiAdapter(
            (context, request, view), IViewletManager, name)
        return manager

    def get_viewlet(self, context, name='collective.cover.resources'):
        manager = self.get_viewlet_manager(context)
        manager.update()
        viewlet = [v for v in manager.viewlets if v.__name__ == name]
        assert len(viewlet) == 1  # nosec
        return viewlet[0]

    def test_viewlet(self):
        html = etree.HTML(self.viewlet())
        self.assertIn('defer', html.xpath('//script')[0].attrib)
        # script name must include the hash of latest git commit
        regexp = r'cover-[\da-f]{7}\.js$'
        self.assertRegexpMatches(
            html.xpath('//script')[0].attrib['src'], regexp)
        regexp = r'cover-[\da-f]{7}\.css$'
        self.assertRegexpMatches(
            html.xpath('//link')[0].attrib['href'], regexp)
