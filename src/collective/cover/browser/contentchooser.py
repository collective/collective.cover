# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.cover.controlpanel import ICoverSettings
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.root import getNavigationRoot
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm

import json


VOCAB_ID = u'plone.app.vocabularies.ReallyUserFriendlyTypes'
ITEMS_BY_REQUEST = 20


class SelectContent(BrowserView):

    """Contentchooser for selecting."""

    index = ViewPageTemplateFile('templates/content_contentchooser.pt')

    def post_url(self):
        return self.context.absolute_url() + '/@@content-search'

    def __call__(self):
        return self.index()


class ContentSearch(BrowserView):

    """Returns the html with the list of results and icons."""

    list_template = ViewPageTemplateFile('templates/search_list.pt')
    tree_template = ViewPageTemplateFile('templates/tree_template.pt')

    def setup(self):
        self.query = self.request.get('q', None)
        self.tab = self.request.get('tab', None)
        page = int(self.request.get('page', 1))
        strategy = SitemapNavtreeStrategy(self.context)

        uuids = None
        result = self.search(
            self.query, uuids=uuids,
            page=page
        )
        self.has_next = result.next is not None
        self.nextpage = result.pagenumber + 1
        children = [strategy.decoratorFactory({'item': node}) for node in result]
        self.level = 1
        self.children = children

    def search(self, query=None, page=1, b_size=ITEMS_BY_REQUEST, uuids=None):
        # XXX uuids parameter not used anywhere
        catalog = api.portal.get_tool('portal_catalog')
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        searchable_types = settings.searchable_content_types

        # temporary we'll only list published elements
        catalog_query = {'sort_on': 'effective', 'sort_order': 'descending'}
        catalog_query['portal_type'] = searchable_types
        if query:
            catalog_query['Title'] = u'{0}*'.format(safe_unicode(query))
        results = catalog(**catalog_query)
        self.total_results = len(results)
        start = (page - 1) * b_size
        results = Batch(results, size=b_size, start=start, orphan=0)
        return results

    def getTermByBrain(self, brain, real_value=True):
        portal_tool = api.portal.get_tool('portal_url')
        self.portal_path = portal_tool.getPortalPath()
        value = brain.getPath()[len(self.portal_path):]
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title)

    def render(self):
        return self.list_template()

    def __call__(self):
        self.setup()
        return self.render()


class SearchItemsBrowserView(BrowserView):

    """Returns a folderish like listing in JSON."""

    def __init__(self, context, request, **kwargs):
        """ Contructor """
        self.context = context
        self.request = request
        util = api.content.get_view(u'plone_layout', self.context, self.request)
        self.getIcon = util.getIcon

        # check if object is a folderish object, if not, get it's parent.
        if not IFolderish.providedBy(self.context):
            self.obj = aq_parent(self.context)
        else:
            self.obj = aq_inner(self.context)

    def _getCurrentValues(self):
        """Return enabled portal types"""
        vocab = queryUtility(IVocabularyFactory, name=VOCAB_ID)(self.context)
        portal_types = api.portal.get_tool('portal_types')
        result = []
        # the vocabulary returns the values sorted by their translated title
        for term in vocab._terms:
            value = portal_types[term.value].id  # portal_type
            title = safe_unicode(term.title)  # already translated title
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

    def jsonByType(self, rooted, document_base_url, searchtext, page='1'):
        """ Returns the actual listing """
        catalog_results = []
        results = {}

        obj = self.obj
        catalog = api.portal.get_tool('portal_catalog')
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
            catalog_query['Title'] = '{0}*'.format(searchtext)

        brains = catalog(**catalog_query)
        page = int(page, 10)
        start = (page - 1) * ITEMS_BY_REQUEST
        brains = Batch(brains, size=ITEMS_BY_REQUEST, start=start, orphan=0)

        results['has_next'] = brains.next is not None
        results['nextpage'] = brains.pagenumber + 1
        results['total_results'] = len(brains)

        for brain in brains:
            catalog_results.append({
                'id': brain.getId,
                'uuid': brain.UID or None,  # Maybe Missing.Value
                'url': brain.getURL(),
                'portal_type': brain.portal_type,
                'normalized_type': normalizer.normalize(brain.portal_type),
                'classicon': 'contenttype-{0}'.format(normalizer.normalize(brain.portal_type)),
                'r_state': 'state-{0}'.format(normalizer.normalize(brain.review_state or '')),
                'title': brain.Title == '' and brain.id or brain.Title,
                'icon': self.getIcon(brain).url or '',
                'is_folderish': brain.is_folderish,
                'description': brain.Description or ''
            })
        # add catalog_ressults
        results['items'] = catalog_results
        # return results in JSON format
        return json.dumps(results)
