# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface

from plone.app.registry.browser import controlpanel

from collective.cover import _
from collective.cover.config import DEFAULT_SEARCHABLE_CONTENT_TYPES


class ICoverSettings(Interface):
    """ Interface for the control panel form.
    """

    layouts = schema.Dict(
        title=_(u"Layouts"),
        required=True,
        key_type=schema.TextLine(title=_(u'Name')),
        value_type=schema.TextLine(title=_(u'Layout')),
        readonly=True,)  # FIXME: we have no widget for this field yet

    searchable_content_types = schema.List(
        title=_(u"Searchable Content Types"),
        description=_(u"Only objects of these content types will be searched "
                      u"on the screenlet."),
        required=False,
        default=DEFAULT_SEARCHABLE_CONTENT_TYPES,
        # we are going to list only the main content types in the widget
        value_type=schema.Choice(
            vocabulary=u'collective.cover.AvailableContentTypes'),)


class CoverSettingsEditForm(controlpanel.RegistryEditForm):
    schema = ICoverSettings
    label = _(u'Cover Settings')
    description = _(u'Settings for the collective.cover package')

    #def updateFields(self):
        #super(CoverSettingsEditForm, self).updateFields()
        #self.fields['layouts'].widgetFactory = TextLinesFieldWidget

    def updateWidgets(self):
        super(CoverSettingsEditForm, self).updateWidgets()
        self.widgets['searchable_content_types'].style = u'min-width: 200px;'


class CoverSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = CoverSettingsEditForm
