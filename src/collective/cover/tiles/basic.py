# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
from plone import api
from plone.autoform import directives as form
from plone.memoize.instance import memoizedproperty
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements
from collective.cover.interfaces import ISearchableText


class IBasicTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )

    image = NamedImage(
        title=_(u'Image'),
        required=False,
    )

    form.omitted('date')
    form.no_omit(IDefaultConfigureForm, 'date')
    date = schema.Datetime(
        title=_(u'Date'),
        required=False,
        readonly=False,
    )

    form.omitted('subjects')
    form.no_omit(IDefaultConfigureForm, 'subjects')
    form.widget(subjects='z3c.form.browser.textarea.TextAreaFieldWidget')
    subjects = schema.Tuple(
        title=_(u'label_categories', default=u'Categories'),
        required=False,
        value_type=schema.TextLine(),
        missing_value=(),
    )

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


class BasicTile(PersistentCoverTile):

    implements(IBasicTile)

    index = ViewPageTemplateFile('templates/basic.pt')

    is_configurable = True
    short_name = _(u'msg_short_name_basic', default=u'Basic')

    @memoizedproperty
    def brain(self):
        catalog = api.portal.get_tool('portal_catalog')
        uuid = self.data.get('uuid')
        result = catalog(UID=uuid) if uuid is not None else []
        assert len(result) <= 1
        return result[0] if result else None

    def Date(self):
        # self.brain is None when the tile was populated by editing it
        if self.brain is not None:
            return super(BasicTile, self).Date(self.brain)

    def is_empty(self):
        return self.brain is None and \
            not [i for i in self.data.values() if i]

    def getURL(self):
        """ Return the URL of the original object.
        """
        if self.brain is not None:
            return self.brain.getURL()

    def Subject(self):
        """ Return the categories of the original object (AKA keywords, tags
            or labels).
        """
        if self.brain is not None:
            return self.brain.Subject

    def populate_with_object(self, obj):
        super(BasicTile, self).populate_with_object(obj)

        # initialize the tile with all fields needed for its rendering
        # note that we include here 'date' and 'subjects', but we do not
        # really care about their value: they came directly from the catalog
        # brain
        data = {
            'title': safe_unicode(obj.Title()),
            'description': safe_unicode(obj.Description()),
            'uuid': IUUID(obj, None),  # XXX: can we get None here? see below
            'date': True,
            'subjects': True,
            'image': self.get_image_data(obj)
        }

        if data['image']:
            # clear scales if new image is getting saved
            self.clear_scales()

        data_mgr = ITileDataManager(self)
        data_mgr.set(data)


class SearchableBasicTile(object):
    implements(ISearchableText)

    def __init__(self, context):
        self.context = context

    def SearchableText(self):
        context = self.context
        return u'{0} {1}'.format(context.data['title'] or '', context.data['description'] or '')
