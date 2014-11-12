# -*- coding: utf-8 -*-

from collective.cover.widgets.interfaces import ITextLinesSortableWidget
from plone.app.uuid.utils import uuidToObject
from z3c.form import interfaces
from z3c.form import widget
from z3c.form.browser import textlines
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

import zope.interface


class TextLinesSortableWidget(textlines.TextLinesWidget):
    """ Widget for adding new keywords and autocomplete with the ones in the
    system.
    """
    zope.interface.implementsOnly(ITextLinesSortableWidget)
    klass = u'textlines-sortable-widget'
    configure_template = ViewPageTemplateFile('textlines_sortable_configure.pt')
    display_template = ViewPageTemplateFile('textlines_sortable_display.pt')
    input_template = ViewPageTemplateFile('textlines_sortable_input.pt')

    def render(self):
        if self.mode == interfaces.DISPLAY_MODE:
            return self.display_template(self)
        elif self.mode == interfaces.INPUT_MODE:
            return self.input_template(self)
        else:  # configure mode
            return self.configure_template(self)

    def sort_results(self):
        """ Returns a sorted list of the stored objects

        :returns: A sorted list of objects
        """
        uuids = self.context['uuids']
        if uuids:
            ordered_uuids = [(k, v) for k, v in uuids.items()]
            ordered_uuids.sort(key=lambda x: x[1]['order'])
            return [{'obj': uuidToObject(x[0]), 'uuid': x[0]}
                    for x in ordered_uuids]
        else:
            return []

    def thumbnail(self, item):
        """ Returns the 'tile' scale for the image added to the item

        :param item: [required] The object to take the image from
        :type item: Content object
        :returns: The <img> tag for the scale
        """
        scales = item.restrictedTraverse('@@images')
        try:
            return scales.scale('image', 'tile')
        except:
            return None

    def get_custom_title(self, uuid):
        """ Returns the custom Title assigned to a specific item

        :param uuid: [required] The object's UUID
        :type uuid: string
        :returns: The custom Title
        """
        title = u''
        uuids = self.context['uuids']
        if uuid in uuids:
            values = uuids.get(uuid)
            title = values.get('custom_title', u'')
        return title

    def get_custom_description(self, uuid):
        """ Returns the custom Description assigned to a specific item

        :param uuid: [required] The object's UUID
        :type uuid: string
        :returns: The custom Description
        """
        description = u''
        uuids = self.context['uuids']
        if uuid in uuids:
            values = uuids.get(uuid)
            description = values.get('custom_description', u'')
        return description

    def get_custom_url(self, uuid):
        """ Returns the custom URL assigned to a specific item

        :param uuid: [required] The object's UUID
        :type uuid: string
        :returns: The custom URL
        """
        url = u''
        uuids = self.context['uuids']
        if uuid in uuids:
            values = uuids.get(uuid)
            url = values.get('custom_url', u'')
        return url

    def extract(self):
        """ Extracts the data from the HTML form and returns it

        :returns: A dictionary with the information
        """
        values = self.request.get(self.name).split('\r\n')
        uuids = [i for i in values if i]
        results = dict()
        for index, uuid in enumerate(uuids):
            custom_title = self.request.get(
                '{0}.custom_title.{1}'.format(self.name, uuid), ''
            )
            custom_description = self.request.get(
                '{0}.custom_description.{1}'.format(self.name, uuid), ''
            )
            custom_url = self.request.get(
                '{0}.custom_url.{1}'.format(self.name, uuid), ''
            )
            results[uuid] = {
                u'order': unicode(index),
                u'custom_title': unicode(custom_title),
                u'custom_description': unicode(custom_description),
                u'custom_url': unicode(custom_url)
            }
        return results


@zope.interface.implementer(interfaces.IFieldWidget)
def TextLinesSortableFieldWidget(field, request):
    """IFieldWidget factory for TextLinesWidget."""
    return widget.FieldWidget(field, TextLinesSortableWidget(request))
