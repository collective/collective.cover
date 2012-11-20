# -*- coding: utf-8 -*-

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


class CollectionTile(PersistentCoverTile):

    index = ViewPageTemplateFile("templates/collection.pt")

    is_configurable = True
    is_editable = False
    configured_fields = []

    def get_title(self):
        return self.data['title']

    def results(self):
        self.configured_fields = self.get_configured_fields()
        size_conf = [i for i in self.configured_fields if i['id'] == 'number_to_show']

        if size_conf and 'size' in size_conf[0].keys():
            size = int(size_conf[0]['size'])
        else:
            size = 4

        uuid = self.data.get('uuid', None)
        if uuid is not None:
            obj = uuidToObject(uuid)
            return obj.results(batch=False)[:size]
        else:
            return []

    def is_empty(self):
        return self.data.get('uuid', None) is None

    def populate_with_object(self, obj):
        super(CollectionTile, self).populate_with_object(obj)  # check permission

        if obj.portal_type in self.accepted_ct():
            title = obj.Title()
            description = obj.Description()
            uuid = IUUID(obj)

            data_mgr = ITileDataManager(self)
            data_mgr.set({'title': title,
                          'description': description,
                          'uuid': uuid,
                          })

    def accepted_ct(self):
        """ Return a list of content types accepted by the tile.
        """
        return ['Collection']

    # TODO: add deprecation warning
    def has_data(self):
        return not self.is_empty()

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
