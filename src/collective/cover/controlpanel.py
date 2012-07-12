# -*- coding: utf-8 -*-

from zope import schema

#from z3c.form.browser.textlines import TextLinesFieldWidget
from zope.interface import Interface

from plone.app.registry.browser import controlpanel

from collective.cover import _


class ICoverSettings(Interface):
    """
    Interface for the control panel form.
    """

    layouts = schema.Dict(
                    title=_(u'Layouts'),
                    key_type=schema.TextLine(title=_(u'Name')),
                    value_type=schema.TextLine(title=_(u'Layout')),)


class CoverSettingsEditForm(controlpanel.RegistryEditForm):
    schema = ICoverSettings
    label = _(u'cover Settings')
    description = _(u'Settings for the collective.cover package')

    #def updateFields(self):
        #super(CoverSettingsEditForm, self).updateFields()
        #self.fields['layouts'].widgetFactory = TextLinesFieldWidget

    #def updateWidgets(self):
        #super(CoverSettingsEditForm, self).updateWidgets()
        #self.widgets['layouts'].rows = 8
        #self.widgets['layouts'].style = u'width: 30%;'


class CoverSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = CoverSettingsEditForm
