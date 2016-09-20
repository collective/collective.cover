# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.config import DEFAULT_AVAILABLE_TILES
from collective.cover.config import DEFAULT_GRID_SYSTEM
from collective.cover.config import DEFAULT_SEARCHABLE_CONTENT_TYPES
from plone.app.registry.browser import controlpanel
from plone.autoform import directives as form
from plone.supermodel import model
from zope import schema


class ICoverSettings(model.Schema):
    """ Interface for the control panel form.
    """

    layouts = schema.Dict(
        title=_(u'Layouts'),
        required=True,
        key_type=schema.TextLine(title=_(u'Name')),
        value_type=schema.TextLine(title=_(u'Layout')),
        readonly=True,  # FIXME: we have no widget for this field yet
    )

    available_tiles = schema.List(
        title=_(u'Available tiles'),
        description=_(u'This tiles will be available for layout creation.'),
        required=True,
        default=DEFAULT_AVAILABLE_TILES,
        value_type=schema.Choice(
            vocabulary='collective.cover.EnabledTiles'),
    )

    searchable_content_types = schema.List(
        title=_(u'Searchable Content Types'),
        description=_(u'Only objects of these content types will be searched '
                      u'on the content chooser.'),
        required=False,
        default=DEFAULT_SEARCHABLE_CONTENT_TYPES,
        # we are going to list only the main content types in the widget
        value_type=schema.Choice(
            vocabulary='collective.cover.AvailableContentTypes'),
    )

    form.widget(styles='z3c.form.browser.textlines.TextLinesFieldWidget')
    styles = schema.Set(
        title=_(u'Styles'),
        description=_(
            u'Enter a list of styles to appear in the style pulldown. '
            u'Format is title|className, one per line.'),
        required=False,
        default=set(),
        value_type=schema.ASCIILine(title=_(u'CSS Class')),
    )

    grid_system = schema.Choice(
        title=_(u'Grid System'),
        description=_(u'Choose a grid system'),
        required=True,
        default=DEFAULT_GRID_SYSTEM,
        vocabulary='collective.cover.GridSystems',
    )


class CoverSettingsEditForm(controlpanel.RegistryEditForm):
    schema = ICoverSettings
    label = _(u'Cover Settings')
    description = _(u'Settings for the collective.cover package')

    # def updateFields(self):
    #     super(CoverSettingsEditForm, self).updateFields()
    #     self.fields['layouts'].widgetFactory = TextLinesFieldWidget

    def updateWidgets(self):
        super(CoverSettingsEditForm, self).updateWidgets()
        self.widgets['available_tiles'].style = u'min-width: 200px;'
        self.widgets['searchable_content_types'].style = u'min-width: 200px;'
        self.widgets['styles'].rows = 6
        self.widgets['styles'].style = u'max-width: 250px;'


class CoverSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = CoverSettingsEditForm
