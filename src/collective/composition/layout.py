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

    pagelayout = ViewPageTemplateFile('layout_templates/pagelayout.pt')
    row = ViewPageTemplateFile('layout_templates/row.pt')
    group = ViewPageTemplateFile('layout_templates/group.pt')
    tile = ViewPageTemplateFile('layout_templates/tile.pt')
    generalmarkup = ViewPageTemplateFile('layout_templates/generalmarkup.pt')

    def get_layout(self):
        layout = json.loads(self.context.composition_layout)

        return layout

    def render_section(self, section, mode):
        if 'type' in section:
            if section['type'] == u'row':
                return self.row(section=section, mode=mode)
            if section['type'] == u'group':
                return self.group(section=section, mode=mode)
            if section['type'] == u'tile':
                return self.tile(section=section, mode=mode)
        else:
            return self.generalmarkup(section=section, mode=mode)

    def is_user_allowed_in_group(self):
        return True

    def tile_is_configurable(self, tile_type):
        return True

    def render_view(self):
        # XXX: There *must* be a better way of doing this, maybe write it
        #      in the request ? sending it as parameter is way too ugly
        return self.pagelayout(mode="view")

    def render_compose(self):
        # XXX: There *must* be a better way of doing this, maybe write it
        #      in the request ? sending it as parameter is way too ugly
        return self.pagelayout(mode="compose")

    def render_layout_edit(self):
        # XXX: There *must* be a better way of doing this, maybe write it
        #      in the request ? sending it as parameter is way too ugly
        return self.pagelayout(mode="layout_edit")

    def accepted_ct_for_tile(self, tile_type):
        tile = self.context.restrictedTraverse(str(tile_type))
        accepted_ct = tile.accepted_ct()

        return json.dumps(accepted_ct)


class LayoutSave(grok.View):
    grok.context(IComposition)
    grok.name('save_layout')
    grok.require('zope2.View')

    def save(self):
        composition_layout = self.request.get('composition_layout')
        self.context.composition_layout = composition_layout
        self.context.reindexObject()

        return composition_layout
        
    def render(self):
        save = self.save()
        return 'saved'
