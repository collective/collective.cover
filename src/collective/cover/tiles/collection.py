# -*- coding: utf-8 -*-

from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.edit import ICoverTileEditView
from plone.app.uuid.utils import uuidToObject
from plone.directives import form
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import queryUtility
from zope.schema import getFieldsInOrder


class ICollectionTile(IPersistentCoverTile, form.Schema):

    title = schema.TextLine(title=u'Title')

    form.omitted('description')
    description = schema.Text(
        title=u'Description',
        required=False,
    )

    form.omitted('date')
    date = schema.Datetime(
        title=u'Date',
        required=False,
    )

    form.omitted('image')
    image = NamedImage(
        title=u'Image',
        required=False,
    )

    form.omitted('number_to_show')
    number_to_show = schema.List(
        title=u'number of elements to show',
        value_type=schema.TextLine(),
        required=False,
    )

    footer = schema.TextLine(title=u'Footer Text')

    uuid = schema.TextLine(title=u'Collection uuid', readonly=True)


class CollectionTile(PersistentCoverTile):

    index = ViewPageTemplateFile("templates/collection.pt")

    is_configurable = True
    is_editable = True
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
        obj = uuidToObject(uuid)
        if uuid and obj:
            return obj.results(batch=False)[:size]
        else:
            self.remove_relation()
            return []

    def is_empty(self):
        return self.data.get('uuid', None) is None or \
            uuidToObject(self.data.get('uuid')) is None

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

    def thumbnail(self, item):
        scales = item.restrictedTraverse('@@images')
        try:
            return scales.scale('image', 'mini')
        except:
            return None

    def remove_relation(self):
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        if 'uuid' in old_data:
            old_data.pop('uuid')
        data_mgr.set(old_data)

    def collection_url(self):
        url = ''
        uuid = self.data.get('uuid', None)
        obj = uuidToObject(uuid)
        if obj:
            url = obj.absolute_url()
        return url

    def show_footer(self):
        conf = self.get_tile_configuration()
        show = conf.get('footer', {}).get('visibility') == 'on'
        return show
