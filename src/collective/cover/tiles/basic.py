# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.interfaces import ISearchableText
from collective.cover.logger import logger
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
from zope.interface import implementer


class IBasicTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )

    form.omitted(IDefaultConfigureForm, 'remote_url')
    remote_url = schema.URI(
        title=_(u'label_remote_url', default=u'URL'),
        description=_(
            u'help_remote_url',
            default=u'Leave this field empty to use the URL of the referenced content. '
                    u'Enter a URL to override it (use absolute links only).'),
        required=False,
    )

    image = NamedImage(
        title=_(u'Image'),
        required=False,
    )

    form.omitted(IDefaultConfigureForm, 'alt_text')
    alt_text = schema.TextLine(
        title=_(
            u'label_alt_text',
            default=u'Alternative Text'),
        description=_(
            u'help_alt_text',
            default=u'Provides a textual alternative to non-text content in web pages.'),  # noqa E501
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


@implementer(IBasicTile)
class BasicTile(PersistentCoverTile):

    index = ViewPageTemplateFile('templates/basic.pt')
    is_configurable = True
    short_name = _(u'msg_short_name_basic', default=u'Basic')

    @memoizedproperty
    def brain(self):
        uuid = self.data.get('uuid')
        results = api.content.find(UID=uuid)
        assert len(results) <= 1  # nosec
        return results[0] if results else None

    def Date(self):
        # self.brain is None when the tile was populated by editing it
        if self.brain:
            return super(BasicTile, self).Date(self.brain)

    def is_empty(self):
        """Check if there is content to be shown respecting permissions."""
        if self.brain:
            return False

        # we have two different use cases here:
        # * the user has no permission to access the content (e.g. Private state)
        # * the tile was manually populated without dropping content on it
        catalog = api.portal.get_tool('portal_catalog')
        uuid = self.data.get('uuid')
        results = catalog.unrestrictedSearchResults(UID=uuid)
        assert len(results) <= 1
        if results:
            return True  # user has no permission to access the content

        # check if tile was manually populated
        return not [i for i in self.data.values() if i]

    def getURL(self):
        """Return the URL of the referenced object or the value stored
        in remote_url field.
        """
        remote_url = self.data.get('remote_url')
        if remote_url:
            return remote_url

        if self.brain:
            return self.brain.getURL()

    def Subject(self):
        """ Return the categories of the original object (AKA keywords, tags
            or labels).
        """
        if self.brain:
            return self.brain.Subject

    def populate_with_object(self, obj):
        super(BasicTile, self).populate_with_object(obj)

        title = safe_unicode(obj.Title())
        description = safe_unicode(obj.Description())

        image = self.get_image_data(obj)
        if image:
            # clear scales if new image is getting saved
            self.clear_scales()

        # initialize the tile with all fields needed for its rendering
        # note that we include here 'date' and 'subjects', but we do not
        # really care about their value: they came directly from the catalog
        # brain
        data = {
            'title': title,
            'description': description,
            'uuid': IUUID(obj),
            'date': True,
            'subjects': True,
            'image': image,
            # FIXME: https://github.com/collective/collective.cover/issues/778
            'alt_text': description or title,
        }

        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

        msg = 'tile "{0}"" populated with data: {1}'
        logger.debug(msg.format(self.id, data))

    @property
    def alt(self):
        """Return alternative text dealing with form init issues."""
        alt_text = self.data['alt_text']
        return alt_text if alt_text is not None else u''


@implementer(ISearchableText)
class SearchableBasicTile(object):

    def __init__(self, context):
        self.context = context

    def SearchableText(self):
        context = self.context
        return u'{0} {1}'.format(
            context.data['title'] or '', context.data['description'] or '')
