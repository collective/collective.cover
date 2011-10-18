import sys

from five import grok
from plone.directives import dexterity, form

from zope.component import getAdapter

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext

from collective.composition.layout import ICompositionLayout

from collective.composition.page_fragment import IPageFragment

from collective.composition import MessageFactory as _


class IComposition(form.Schema):
    """
    Composable page
    """
    form.model("models/composition.xml")


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
            if not IPageFragment.implementedBy(klass):
                continue
            expression = Expression(type_info.icon_expr)
            expression_context = getExprContext(self)
            icon = expression(expression_context)
            available.append({'portal_type': dotted,
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
    

class Compose(grok.View):
    grok.context(IComposition)
    grok.require('zope2.View')
    
    def render_context_menus(self):
        widget_template = """
                {label:'%(title)s',
                 icon:'%(icon)s',
                 action:function() { alert('Add %(portal_type)s'); }
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
            menus += menu_template % (slot, widgets)
        menus += """
            })"""
        return menus

