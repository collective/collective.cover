# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.cover.controlpanel import ICoverSettings
from five import grok
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.root import getNavigationRoot
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from Products.Five.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from Products.CMFPlone.PloneBatch import Batch

import json

VOCAB_ID = u'plone.app.vocabularies.ReallyUserFriendlyTypes'

grok.templatedir('contentchooser_templates')


# XXX: what's the purpose of this view?
#      why is here if it's intendes for tests?
#      can we get rid of it?
class TestContent(grok.View):
    """
    test contentchooser for selecting
    """
    grok.context(Interface)
    grok.name('test-content-contentchooser')
    grok.require('zope2.View')
    grok.template('test_content_contentchooser')


class SelectContent(grok.View):
    """
    contentchooser for selecting
    """
    grok.context(Interface)
    grok.name('select-content-contentchooser')
    grok.require('zope2.View')
    grok.template('content_contentchooser')

    def update(self):
        pass

    def post_url(self):
        return self.context.absolute_url() + '/@@content-search'


class ContentSearch(grok.View):
    """
    returns the html with the list of results and icons
    """
    grok.context(Interface)
    grok.name('content-search')
    grok.require('zope2.View')

    list_template = ViewPageTemplateFile('contentchooser_templates/search_list.pt')
    tree_template = ViewPageTemplateFile('contentchooser_templates/tree_template.pt')

    def update(self):
        self.query = self.request.get('q', None)
        self.tab = self.request.get('tab', None)
        b_size = int(self.request.get('b_size', 10))
        page = int(self.request.get('page', 0))
        strategy = SitemapNavtreeStrategy(self.context)

        uids = None
        result = self.search(self.query, uids=uids,
                             page=page,
                             b_size=b_size)
        self.has_next = result.next is not None
        self.nextpage = result.pagenumber + 1
        result = [strategy.decoratorFactory({'item': node}) for node in result]
        self.level = 1
        self.children = result

    def render(self):
        return self.list_template(children=self.children, level=1)

    def search(self, query=None, page=0, b_size=10, uids=None):
        catalog = getToolByName(self.context, 'portal_catalog')
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        searchable_types = settings.searchable_content_types

        #temporary we'll only list published elements
        catalog_query = {'sort_on': 'effective', 'sort_order': 'descending'}
        catalog_query['portal_type'] = searchable_types

        if query:
            catalog_query = {'SearchableText': u'{0}*'.format(query)}

        # XXX: not implemented, this is needed?
#        if uids:
#            catalog_query['UID'] = uids

        results = catalog(**catalog_query)
        results = Batch(results, size=b_size, start=(page * b_size), orphan=0)

        return results

    def getTermByBrain(self, brain, real_value=True):
        portal_tool = getToolByName(self.context, 'portal_url')
        self.portal_path = portal_tool.getPortalPath()
        value = brain.getPath()[len(self.portal_path):]
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title)


class SearchItemsBrowserView(BrowserView):
    """ Returns a folderish like listing in JSON """

    def __init__(self, context, request, **kwargs):
        """ Contructor """
        self.context = context
        self.request = request
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.plone_view = getMultiAdapter((self.context, self.request),
                                          name=u'plone')
        self.getIcon = self.plone_view.getIcon
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(ICoverSettings)

        # check if object is a folderish object, if not, get it's parent.
        if not IFolderish.providedBy(self.context):
            self.obj = aq_parent(self.context)
        else:
            self.obj = aq_inner(self.context)

    def _getCurrentValues(self):
        """Return enabled portal types"""
        vocab = queryUtility(IVocabularyFactory, name=VOCAB_ID)(self.context)
        portal_types = getToolByName(self.context, 'portal_types', None)
        result = []
        # the vocabulary returns the values sorted by their translated title
        for term in vocab._terms:
            value = portal_types[term.value].id  # portal_type
            title = unicode(term.title)  # already translated title
            result.append((value, title))

        return result

    def getBreadcrumbs(self, path=None):
        """ Get breadcrumbs """
        result = []
        root_url = getNavigationRoot(self.obj)
        root = aq_inner(self.obj.restrictedTraverse(root_url))
        root_url = root.absolute_url()

        if path is not None:
            root_abs_url = root.absolute_url()
            path = path.replace(root_abs_url, '', 1)
            path = path.strip('/')
            root = aq_inner(root.restrictedTraverse(path))

        relative = aq_inner(self.obj).getPhysicalPath()[len(root.getPhysicalPath()):]
        if path is None:
            # Add siteroot
            result.append({'title': root.title_or_id(),
                           'url': '/'.join(root.getPhysicalPath())})

        for i in range(len(relative)):
            now = relative[:i + 1]
            obj = aq_inner(root.restrictedTraverse(now))

            if IFolderish.providedBy(obj):
                if not now[-1] == 'talkback':
                    result.append({'title': obj.title_or_id(),
                                   'url': root_url + '/' + '/'.join(now)})
        return result

    def jsonByType(self, rooted, document_base_url, searchtext):
        """ Returns the actual listing """
        catalog_results = []
        results = {}

        obj = self.obj
        portal_catalog = getToolByName(obj, 'portal_catalog')
        normalizer = getUtility(IIDNormalizer)

        if 'filter_portal_types' in self.request.keys():
            self.filter_portal_types = self.request['filter_portal_types']
        else:
            self.filter_portal_types = [i[0] for i in self._getCurrentValues()]

        if INavigationRoot.providedBy(obj) or (rooted == 'True' and document_base_url[:-1] == obj.absolute_url()):
            results['parent_url'] = ''
        else:
            results['parent_url'] = aq_parent(obj).absolute_url()
        if rooted == 'True':
            results['path'] = self.getBreadcrumbs(results['parent_url'])
        else:
            # get all items from siteroot to context (title and url)
            results['path'] = self.getBreadcrumbs()
        # get all portal types and get information from brains
        path = '/'.join(obj.getPhysicalPath())

        catalog_query = {'sort_on': 'getObjPositionInParent'}
        catalog_query['portal_type'] = self.filter_portal_types
        catalog_query['path'] = {'query': path, 'depth': 1}
        if searchtext:
            catalog_query = {'SearchableText': '{0}*'.format(searchtext)}

        for brain in portal_catalog(**catalog_query):
            catalog_results.append({
                'id': brain.getId,
                'uid': brain.UID or None,  # Maybe Missing.Value
                'url': brain.getURL(),
                'portal_type': brain.portal_type,
                'normalized_type': normalizer.normalize(brain.portal_type),
                'classicon': 'contenttype-{0}'.format(normalizer.normalize(brain.portal_type)),
                'r_state': 'state-{0}'.format(normalizer.normalize(brain.review_state or '')),
                'title': brain.Title == "" and brain.id or brain.Title,
                'icon': self.getIcon(brain).html_tag() or '',
                'is_folderish': brain.is_folderish})
        # add catalog_ressults
        results['items'] = catalog_results
        # return results in JSON format
        return json.dumps(results)
