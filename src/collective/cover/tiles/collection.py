# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.directives import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from z3c.form.interfaces import IDisplayForm
from z3c.form.interfaces import IEditForm

from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile

from collective.cover.tiles.edit import ICoverTileEditView

class ICollectionTile(IPersistentCoverTile, form.Schema):

    title = schema.TextLine(title=u'Title')
    
    form.omitted(ICoverTileEditView, 'description')
    description = schema.Text(
        title=u'Description',
        required=False,
        )
      
    form.omitted(ICoverTileEditView, 'date')  
    date = schema.Datetime(
        title=u'Date',
        required=False,
        )

    form.omitted(ICoverTileEditView, 'image')
    image = NamedImage(
        title=u'Image',
        required=False,
        )
        
    form.omitted(ICoverTileEditView, 'number_to_show')
    number_to_show = schema.List(
        title=u'number of elements to show',
        value_type=schema.TextLine(),
        required=False,
        )

    uuid = schema.TextLine(title=u'Collection uuid', readonly=True)

    def results():
        """
        This method return a list og
        A method to return the rich text stored in the tile
        """

    def populate_with_object(obj):
        """
        This method will take a CT Collection as parameter, and it will store a
        reference to it.
        """

    def delete():
        """
        This method removes the persistent data created for this tile
        """

    def accepted_ct():
        """
        Return a list of supported content types.
        """

    def has_data():
        """
        A method that return True if the tile have a data.
        """


class CollectionTile(PersistentCoverTile):

    index = ViewPageTemplateFile("templates/collection.pt")

    is_configurable = True
    is_editable = False

    def get_title(self):
        return self.data['title']

    def results(self):
        start = 0
        size = 6
        uuid = self.data.get('uuid', None)
        if uuid is not None:
            obj = uuidToObject(uuid)
            return obj.results(b_start=start, b_size=size)

    def populate_with_object(self, obj):
        super(CollectionTile, self).populate_with_object(obj)

        title = obj.Title() or None
        description = obj.Description() or None
        uuid = IUUID(obj, None)

        data_mgr = ITileDataManager(self)

        data_mgr.set({'title': title,
                      'description': description,
                      'uuid': uuid,
                      })

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = ['Collection', ]
        return valid_ct

    def has_data(self):
        self.get_configured_fields()
        uuid = self.data.get('uuid', None)
        return uuid is not None
