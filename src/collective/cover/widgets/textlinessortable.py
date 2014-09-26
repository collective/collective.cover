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
        uuids = self.context['uuids']
        if uuids:
            ordered_uuids = [(k, v) for k, v in uuids.items()]
            ordered_uuids.sort(key=lambda x: x[1]['order'])
            return [{'obj': uuidToObject(x[0]), 'uuid': x[0]}
                    for x in ordered_uuids]
        else:
            return []

    def thumbnail(self, item):
        scales = item.restrictedTraverse('@@images')
        try:
            return scales.scale('image', 'tile')
        except:
            return None

    def get_custom_url(self, uuid):
        url = u''
        uuids = self.context['uuids']
        if uuid in uuids:
            values = uuids.get(uuid)
            url = values.get('custom_url', u'')
        return url

    def extract(self):
        values = self.request.get(self.name).split('\r\n')
        uuids = [i for i in values if i]
        results = dict()
        for index, uuid in enumerate(uuids):
            if uuid:
                custom_url = self.request.get(
                    '%s.custom_url.%s' % (self.name, uuid), ""
                )
                results[uuid] = {
                    u'order': unicode(index),
                    u'custom_url': unicode(custom_url)
                }
        return results


@zope.interface.implementer(interfaces.IFieldWidget)
def TextLinesSortableFieldWidget(field, request):
    """IFieldWidget factory for TextLinesWidget."""
    return widget.FieldWidget(field, TextLinesSortableWidget(request))
