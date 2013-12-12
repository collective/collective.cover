# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from plone import api
from plone.app.tiles.browser.edit import DefaultEditForm
from plone.app.tiles.browser.edit import DefaultEditView
from plone.app.tiles.browser.traversal import EditTile
from plone.app.tiles.utils import appendJSONData
from plone.tiles.interfaces import ITileDataManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.interfaces.browser import IBrowserView
from zope.traversing.browser.absoluteurl import absoluteURL

from collective.cover import _
from collective.cover.interfaces import ITileEditForm


class ICoverTileEditView(IBrowserView):
    """
    """


class CustomEditForm(DefaultEditForm):
    """Standard tile edit form, which is wrapped by DefaultEditView (see
    below).

    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """

    implements(ITileEditForm)

    def update(self):
        super(CustomEditForm, self).update()

        typeName = self.tileType.__name__
        tileId = self.tileId

        tile = self.context.restrictedTraverse('@@{0}/{1}'.format(typeName, tileId))

        if not tile.isAllowedToEdit():
            raise Unauthorized(
                _(u'You are not allowed to add this kind of tile'))

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Traverse to a new tile in the context, with no data
        typeName = self.tileType.__name__
        tile = self.context.restrictedTraverse('@@{0}/{1}'.format(typeName, self.tileId))

        # We need to check first for existing content in order not not loose
        # fields that weren't sent with the form
        dataManager = ITileDataManager(tile)
        old_data = dataManager.get()
        for item in data:
            old_data[item] = data[item]
        dataManager.set(old_data)

        # notify about modification
        notify(ObjectModifiedEvent(tile))
        api.portal.show_message(_(u'Tile saved'), self.request, type='info')

        # Look up the URL - we need to do this after we've set the data to
        # correctly account for transient tiles
        tileURL = absoluteURL(tile, self.request)
        self.request.response.redirect(tileURL)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        tileDataJson = {}
        tileDataJson['action'] = 'cancel'
        url = self.request.getURL()
        url = appendJSONData(url, 'tiledata', tileDataJson)
        self.request.response.redirect(url)


class CustomTileEdit(DefaultEditView):
    """
    Override the default @@edit-tile so we can raise Unauthorized using our
    custom security implementation
    """

    form = CustomEditForm
    index = ViewPageTemplateFile('templates/tileformlayout.pt')


class CoverTileEditView(EditTile):
    """
    Implements the @@edit-tile namespace for our specific tiles, so we can
    check permissions.
    """

    targetInterface = ICoverTileEditView
