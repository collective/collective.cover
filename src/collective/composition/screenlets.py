# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.schema.vocabulary import SimpleTerm

from five import grok

from Products.CMFCore.utils import getToolByName

from collective.composition import _

from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy

from plone.app.layout.navigation.interfaces import INavtreeStrategy

grok.templatedir("screenlets_templates")

class TestContet(grok.View):
    """
    test screenlet for selecting
    """
    grok.context(Interface)
    grok.name('test-content-screenlet')
    grok.require('zope2.View')
    grok.template('test_content_screenlet')
    

class SelectContentScreenlet(grok.View):
    """
    screenlet for selecting
    """
    grok.context(Interface)
    grok.name('select-content-screenlet')
    grok.require('zope2.View')
    grok.template('content_screenlet')
    
    def post_url(self):
        return self.context.absolute_url() + "/@@content-search"
    
class ContentSearch(grok.View):
    """
    returns the html with the list of results and icons
    """
    grok.context(Interface)
    grok.name('content-search')
    grok.require('zope2.View')
    grok.template('search_list')
    
    def update(self):
        query = self.request.get('q', None)
        # if not query:
        #             return ''
        
        result = self.search(query)
        portal_state = getMultiAdapter((self.context, self.request),
                                          name=u'plone_portal_state')
        portal = portal_state.portal()

        strategy = SitemapNavtreeStrategy(self.context)
        
        result = [strategy.decoratorFactory({'item':node}) for node in result]
        self.level = 1
        self.children = result
    
    def search(self, query=None, limit=None, portal_type=None):
        pc = getToolByName(self.context, "portal_catalog")
        catalog_query = {}
        
        if query:
            catalog_query = {'SearchableText': query}

        if limit:
            catalog_query['sort_limit'] = limit
        if portal_type:
            catalog_query['portal_type'] = portal_type
        results =  pc(**catalog_query)
        return results

    def getTermByBrain(self, brain, real_value=True):
        portal_tool = getToolByName(self.context, "portal_url")
        self.portal_path = portal_tool.getPortalPath()
        value = brain.getPath()[len(self.portal_path):]
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title)