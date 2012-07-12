# -*- coding: utf-8 -*-

from zope import schema

#from z3c.form.browser.textlines import TextLinesFieldWidget
from zope.interface import Interface

from plone.app.registry.browser import controlpanel

from collective.composition import _


class ICompositionSettings(Interface):
    """
    Interface for the control panel form.
    """

    layouts = schema.Dict(
                    title=_(u'Layouts'),
                    key_type=schema.TextLine(title=_(u'Name')),
                    value_type=schema.TextLine(title=_(u'Layout')),)


class CompositionSettingsEditForm(controlpanel.RegistryEditForm):
    schema = ICompositionSettings
    label = _(u'Composition Settings')
    description = _(u'Settings for the collective.composition package')

    #def updateFields(self):
        #super(CompositionSettingsEditForm, self).updateFields()
        #self.fields['layouts'].widgetFactory = TextLinesFieldWidget

    #def updateWidgets(self):
        #super(CompositionSettingsEditForm, self).updateWidgets()
        #self.widgets['layouts'].rows = 8
        #self.widgets['layouts'].style = u'width: 30%;'


class CompositionSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = CompositionSettingsEditForm
