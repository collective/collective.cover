# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.schema.vocabulary import SimpleTerm
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from five import grok

from plone.app.layout.navigation.navtree import buildFolderTree

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy

from collective.composition import _

grok.templatedir("screenlets_templates")


class TestContent(grok.View):
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

    def update(self):
        pass

    def post_url(self):
        return self.context.absolute_url() + "/@@content-search"


class ContentSearch(grok.View):
    """
    returns the html with the list of results and icons
    """
    grok.context(Interface)
    grok.name('content-search')
    grok.require('zope2.View')

    list_template = ViewPageTemplateFile('screenlets_templates/search_list.pt')
    tree_template = ViewPageTemplateFile('screenlets_templates/tree_template.pt')

    def update(self):
        query = self.request.get('q', None)
        self.tab = self.request.get('tab', None)
        uids = None
        if self.tab == 'recent':
            pass
        elif self.tab == 'clipboard':
            brains = list(self.search(''))[:2]
            uids = [b.UID for b in brains]
        result = self.search(query, uids=uids)
        strategy = SitemapNavtreeStrategy(self.context)
        result = [strategy.decoratorFactory({'item': node}) for node in result]
        if self.tab == 'content-tree':
            portal_state = getMultiAdapter((self.context, self.request),
                                              name=u'plone_portal_state')
            portal = portal_state.portal()
            query_tree = {'sort_on': 'getObjPositionInParent', 
                'sort_order': 'asc', 'is_default_page': False}
            strategy.rootPath = '/Plone'
            data = buildFolderTree(portal,
                               obj=portal,
                               query=query_tree,
                               strategy=strategy)
            result = data.get('children', [])
        self.level = 1
        self.children = result
    
    def render(self):
        template = self.list_template
        if self.tab == 'content-tree':
            return self.tree_template(children=self.children,
            level=1)
        return self.list_template()


    def search(self, query=None, limit=None, portal_type=None, uids=None):
        pc = getToolByName(self.context, "portal_catalog")
        catalog_query = {}
        if query:
            catalog_query = {'SearchableText': query}
        if limit:
            catalog_query['sort_limit'] = limit
        if portal_type:
            catalog_query['portal_type'] = portal_type
        if uids:
            catalog_query['UID'] = uids
        results = pc(**catalog_query)
        return results

    def getTermByBrain(self, brain, real_value=True):
        portal_tool = getToolByName(self.context, "portal_url")
        self.portal_path = portal_tool.getPortalPath()
        value = brain.getPath()[len(self.portal_path):]
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title)
    
