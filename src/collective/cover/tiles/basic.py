# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements
from zope.component import getUtility

from plone.memoize import view
from plone.memoize.instance import memoizedproperty
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.namedfile.file import NamedBlobImage as NamedImageFile
from plone.registry.interfaces import IRegistry
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID

from z3c.form.browser.textlines import TextLinesFieldWidget

from plone.autoform import directives as form

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.controlpanel import ICoverSettings


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

    date = schema.Datetime(
        title=_(u'Date'),
        required=False,
    )

    subjects = schema.Tuple(
        title=_(u'label_categories', default=u'Categories'),
        description=_(u'help_categories',
                      default=(u"Also known as keywords, tags or labels, "
                               "these help you categorize your content.")),
        required=False,
        value_type=schema.TextLine(),
        missing_value=(),
    )

    form.widget(tags=TextLinesFieldWidget)

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


class BasicTile(PersistentCoverTile):

    implements(IPersistentCoverTile)

    index = ViewPageTemplateFile("templates/basic.pt")

    is_configurable = True

    @memoizedproperty
    def brain(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        uuid = self.data.get('uuid')
        result = catalog(UID=uuid) if uuid is not None else []
        assert len(result) <= 1
        return result[0] if result else None

    def Date(self):
        """ Return the date of publication or modification of the object.
        """
        if self.brain is not None:
            return self.brain.Date

    def is_empty(self):
        return self.brain is not None and not (
            self.data.get('title') or
            self.data.get('description') or
            self.data.get('image')
        )

    def getURL(self):
        if self.brain is not None:
            return self.brain.getURL()

    def populate_with_object(self, obj):
        super(BasicTile, self).populate_with_object(obj)

        data = {
            'title': obj.Title(),
            'description': obj.Description(),
            'uuid': IUUID(obj, None),
        }

        # XXX: Implements a better way to detect image fields.
        # probably detecting if the object is Archetypes or Dexterity first
        try:
            data['image'] = NamedImageFile(str(obj.getImage().data))
        except AttributeError:
            try:
                data['image'] = NamedImageFile(str(obj.image.data))
            except AttributeError:
                pass

        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    @view.memoize
    def accepted_ct(self):
        """
            Return a list with accepted content types ids
            basic tile accepts every content type
            allowed by the cover control panel

            this method is called for every tile in the compose view
            please memoize if you're doing some very expensive calculation
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        return settings.searchable_content_types
