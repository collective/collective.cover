# -*- coding: utf-8 -*-
from interfaces import ICSSClassWidget
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget

import json
import six
import zope.interface
import zope.schema


@zope.interface.implementer_only(ICSSClassWidget)
class CSSClassWidget(SelectWidget):
    """Select widget implementation."""

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(SelectWidget, self).update()
        widget.addFieldClass(self)
        if isinstance(self.context.get('css_class'), six.text_type):
            self.value = [self.context.get('css_class')]

    def options(self):
        items = [
            {
                key: value
                for key, value in six.iteritems(item)
                if key != 'id'
            }
            for item in self.items
            if item['value'] != 'tile-default'
        ]
        return json.dumps(items)

    def selected(self):
        return self.context.get('css_class', 'tile-default')


@zope.component.adapter(zope.schema.interfaces.IChoice,
                        zope.interface.Interface,
                        interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def CSSClassFieldWidget(field, source, request=None):
    """IFieldWidget factory for SelectWidget."""
    # BBB: emulate our pre-2.0 signature (field, request)
    if request is None:
        real_request = source
    else:
        real_request = request
    return FieldWidget(field, CSSClassWidget(real_request))
