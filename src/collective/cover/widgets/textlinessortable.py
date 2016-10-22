# -*- coding: utf-8 -*-
from collective.cover.utils import get_types_use_view_action_in_listings
from collective.cover.utils import uuidToObject
from collective.cover.widgets.interfaces import ITextLinesSortableWidget
from Products.CMFPlone.utils import base_hasattr
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
        if not item:
            return None
        scales = item.restrictedTraverse('@@images')
        try:
            return scales.scale('image', 'tile')
        except:  # FIXME: B901 blind except: statement
            return None

    def isExpired(self, item):
        if base_hasattr(item, 'expires'):
            return item.expires().isPast()
        return False

    def get_custom_title(self, uuid):
        """ Returns the custom Title assigned to a specific item

        :param uuid: [required] The object's UUID
        :type uuid: string
        :returns: The custom Title
        """
        # Try to get custom title
        title = u''
        uuids = self.context['uuids']
        values = [uuids[i] for i in uuids if i == uuid]
        if values:
            title = values[0].get('custom_title', u'')
        if title:
            return title
        # If didn't find, get object title
        obj = uuidToObject(uuid)
        return obj.Title()

    def get_custom_description(self, uuid):
        """ Returns the custom Description assigned to a specific item

        :param uuid: [required] The object's UUID
        :type uuid: string
        :returns: The custom Description
        """
        # Try to get custom description
        description = u''
        uuids = self.context['uuids']
        values = [uuids[i] for i in uuids if i == uuid]
        if values:
            description = values[0].get('custom_description', u'')
        if description:
            return description
        # If didn't find, get object description
        obj = uuidToObject(uuid)
        return obj.Description()

    def get_custom_url(self, uuid):
        """ Returns the custom URL assigned to a specific item

        :param uuid: [required] The object's UUID
        :type uuid: string
        :returns: The custom URL
        """
        # Try to get custom url
        url = u''
        uuids = self.context['uuids']
        values = [uuids[i] for i in uuids if i == uuid]
        if values:
            url = values[0].get('custom_url', u'')
        if url:
            return url
        # If didn't find, get object url
        obj = uuidToObject(uuid)
        url = obj.absolute_url()
        if obj.portal_type in get_types_use_view_action_in_listings():
            url += '/view'
        return url

    def extract(self):
        """ Extracts the data from the HTML form and returns it

        :returns: A dictionary with the information
        """
        values = self.request.get(self.name).splitlines()
        uuids = [i for i in values if i]
        results = dict()
        for index, uuid in enumerate(uuids):
            obj = uuidToObject(uuid)
            results[uuid] = {
                u'order': unicode(index)
            }
            custom_title = self.request.get(
                '{0}.custom_title.{1}'.format(self.name, uuid), ''
            )
            if (custom_title != u'' and
               custom_title != obj.Title().decode('utf-8')):
                results[uuid][u'custom_title'] = unicode(custom_title)
            custom_description = self.request.get(
                '{0}.custom_description.{1}'.format(self.name, uuid), ''
            )
            if (custom_description != u'' and
               custom_description != obj.Description().decode('utf-8')):
                results[uuid][u'custom_description'] = unicode(custom_description)
            custom_url = self.request.get(
                '{0}.custom_url.{1}'.format(self.name, uuid), ''
            )
            url = obj.absolute_url()
            if obj.portal_type in get_types_use_view_action_in_listings():
                url += '/view'
            if (custom_url != u'' and
               custom_url != url):
                results[uuid][u'custom_url'] = unicode(custom_url)
        return results


@zope.interface.implementer(interfaces.IFieldWidget)
def TextLinesSortableFieldWidget(field, request):
    """IFieldWidget factory for TextLinesWidget."""
    return widget.FieldWidget(field, TextLinesSortableWidget(request))
