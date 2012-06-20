# -*- coding: utf-8 -*-
import json

from five import grok

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from collective.composition.composition import IComposition

from collective.composition import _

#grok.templatedirs("layout_templates")


class PageLayout(grok.View):
    """
    Renders a layout for the composition object.
    """
    grok.context(IComposition)
    grok.name('layout')
    grok.require('zope2.View')

    row = ViewPageTemplateFile('layout_templates/row.pt')
    group = ViewPageTemplateFile('layout_templates/group.pt')
    tile = ViewPageTemplateFile('layout_templates/tile.pt')

    def get_layout(self):
        layout = json.loads(self.context.composition_layout)

        return layout

    def render_section(self, section):
        if section['type'] == u'row':
            return self.row(section=section)
        if section['type'] == u'group':
            return self.group(section=section)
        if section['type'] == u'tile':
            return self.tile(section=section)

    def is_user_allowed_in_group(self):
        return True
