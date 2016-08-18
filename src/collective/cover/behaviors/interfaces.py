# coding: utf-8
from collective.cover import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Invalid
from z3c.form import validator


class IRefresh(model.Schema):

    """Reload the current page after a certain amount of time."""

    model.fieldset('settings', fields=['enable_refresh', 'ttl'])

    enable_refresh = schema.Bool(
        title=_(u'Enable refresh'),
        description=_(u'Enable refresh of the current page.'),
        default=False,
    )

    ttl = schema.Int(
        title=_(u'Time to live'),
        description=_(u'Number of seconds after which to reload the current page.',),
        default=300,
    )

class TimeToLiveValidator(validator.SimpleFieldValidator):

    """z3c.form validator class for time to live"""

    def validate(self, value):
        """Validate the value on time to live input"""
        if value <= 0:
            raise Invalid(_(u'Value must be greater than zero.'))

validator.WidgetValidatorDiscriminators(TimeToLiveValidator, field=IRefresh['ttl'])

alsoProvides(IRefresh, IFormFieldProvider)


@form.validator(field=IRefresh['ttl'])
def validate_ttl(value):
    if value <= 0:
        raise Invalid(_(u'Value must be greater than zero.'))
