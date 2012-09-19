# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema

from zope.component import queryUtility

from zope.schema import getFieldsInOrder

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from plone.namedfile.field import NamedBlobImage as NamedImage

from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType

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
    configured_fields = []

    def get_title(self):
        return self.data['title']

    def results(self):
        self.configured_fields = self.get_configured_fields()
        start = 0
        size_conf = [i for i in self.configured_fields if i['id'] == 'number_to_show']
        if size_conf:
            size = int(size_conf[0]['size'])
        else:
            size = 6

        uuid = self.data.get('uuid', None)
        if uuid is not None:
            obj = uuidToObject(uuid)
            return obj.results(batch=False)[:size]

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
        uuid = self.data.get('uuid', None)
        return uuid is not None

    def get_configured_fields(self):
        # Override this method, since we are not storing anything
        # in the fields, we just use them for configuration
        tileType = queryUtility(ITileType, name=self.__name__)
        conf = self.get_tile_configuration()

        fields = getFieldsInOrder(tileType.schema)

        results = []
        for name, obj in fields:
            field = {'id': name,
                     'title': obj.title}
            if name in conf:
                field_conf = conf[name]
                if ('visibility' in field_conf and field_conf['visibility'] == u'off'):
                    # If the field was configured to be invisible, then just
                    # ignore it
                    continue

                if 'htmltag' in field_conf:
                    # If this field has the capability to change its html tag
                    # render, save it here
                    field['htmltag'] = field_conf['htmltag']

                if 'imgsize' in field_conf:
                    field['scale'] = field_conf['imgsize']

                if 'size' in field_conf:
                    field['size'] = field_conf['size']

            results.append(field)

        return results
