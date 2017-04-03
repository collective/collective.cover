# -*- coding: utf-8 -*-

from collective.cover.controlpanel import ICoverSettings
from collective.cover.widgets.interfaces import ISelectPreviewWidget
from plone.registry.interfaces import IRegistry
from z3c.form import interfaces
from z3c.form.browser import select
from z3c.form.widget import FieldWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility

import json
import zope.interface


class SelectPreviewWidget(select.SelectWidget):
    """ Widget for adding new keywords and autocomplete with the ones in the
    system.
    """
    zope.interface.implementsOnly(ISelectPreviewWidget)
    klass = u'keyword-widget'
    display_template = ViewPageTemplateFile('selectpreview_display.pt')
    input_template = ViewPageTemplateFile('selectpreview_input.pt')

    # JavaScript template
    js_template = """\
    (function($) {
        $().ready(function() {
        var layouts = %(layouts)s;
        $.fn.layoutpreview('#%(id)s', layouts);
        });
    })(jQuery);
    """

    def js(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        layouts = settings.layouts

        simple_layouts = {}
        for layout in layouts:
            simplyfied = []
            lay = json.loads(layouts[layout])

            self.simplify_layout(lay, simplyfied)
            simple_layouts[layout] = simplyfied

        return self.js_template % dict(id=self.id, layouts=json.dumps(simple_layouts))

    def render(self):
        if self.mode == interfaces.DISPLAY_MODE:
            return self.display_template(self)
        else:
            return self.input_template(self)

    def simplify_layout(self, layout, simple_layout=[]):
        for element in layout:
            item = {}
            if element['type'] == 'row':
                item['type'] = 'row'

            if element['type'] == 'group':
                item['type'] = 'group'
                item['size'] = element['column-size']

            if element['type'] == 'tile':
                item['type'] = 'tile'
                item['tile-type'] = element['tile-type']

            if 'children' in element:
                item['children'] = []
                simple_layout.append(item)
                self.simplify_layout(element['children'], item['children'])
            else:
                simple_layout.append(item)


@zope.component.adapter(zope.schema.interfaces.IChoice,
                        zope.interface.Interface,
                        interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SelectFieldWidget(field, source, request=None):
    """IFieldWidget factory for SelectWidget."""
    # BBB: emulate our pre-2.0 signature (field, request)
    if request is None:
        real_request = source
    else:
        real_request = request
    return FieldWidget(field, SelectPreviewWidget(real_request))
