import sys

import json

from five import grok
from plone.directives import dexterity, form

from zope.interface import Interface
from zope.component import getAdapter

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext
from plone.dexterity.utils import createContentInContainer

from collective.composition.layout import ICompositionLayout

from collective.composition import MessageFactory as _


class IComposition(form.Schema):
    """
    Composable page
    """
    form.model("models/composition.xml")


class ICompositionFragment(Interface):
    """
    Main interface for fragments
    """


class Composition(dexterity.Container):
    grok.implements(IComposition)
    
    @property
    def current_layout(self):
        layout_name = self.composition_layout
        layout = getAdapter((self,), ICompositionLayout, name=layout_name)
        return layout

    def available_widgets(self):
        types_tool = getToolByName(self, "portal_types")
        types = types_tool.listTypeInfo()
        available = []
        for type_info in types:
            dotted = getattr(type_info, 'klass', None)
            if not dotted:
                continue
            package, klass = dotted.rsplit('.', 1)
            try:
                __import__(package)
            except ImportError:
                continue
            klass = getattr(sys.modules[package], klass, None)
            if not ICompositionFragment.implementedBy(klass):
                continue
            expression = Expression(type_info.icon_expr)
            expression_context = getExprContext(self)
            icon = expression(expression_context)
            available.append({'portal_type': type_info.id,
                              'icon': icon,
                              'title': type_info.title,
                              'description': type_info.description})
        return available

    def render(self):
        layout = self.current_layout
        return layout.render()


class View(grok.View):
    grok.context(IComposition)
    grok.require('zope2.View')
    grok.name('view')
    

class AddCompositionWidget(grok.View):
    grok.context(IComposition)
    grok.require('zope2.View')

    def render(self):
        widget_type = self.request.get('widget_type')
        widget_title = self.request.get('widget_title')
        column_id = self.request.get('column_id')
        widget = createContentInContainer(self.context,
                                          widget_type,
                                          title=widget_title,
                                          checkConstraints=False)
        widget_url = widget.absolute_url()
        return json.dumps({ 'column_id': column_id,
                 'widget_type': widget_type,
                 'widget_title': widget_title,
                 'widget_id': widget.id,
                 'widget_url': widget_url})


class Compose(grok.View):
    grok.context(IComposition)
    grok.require('zope2.View')
    
    def render_context_menus(self):
        widget_template = """
                {label:'%(title)s',
                 icon:'%(icon)s',
                 action:function() { Composition.addWidget('#*slot*', '%(portal_type)s', '%(title)s'); }
                }"""
        widget_list = []
        for widget in self.context.available_widgets():
            widget_list.append(widget_template % widget)
        widgets = ",".join(widget_list)
        menu_template = """
            $('#%s').contextPopup({
              title: 'Add Widgets',
              items: [
              %s
              ]});"""
        menus = """
            jQuery(function($) {"""
        for slot in self.context.current_layout.columns:
            menu = menu_template % (slot, widgets)
            menu = menu.replace('*slot*', slot)
            menus += menu
        menus += """
            })"""
        return menus

