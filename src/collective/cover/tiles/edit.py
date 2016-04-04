# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.cover import _
from collective.cover.interfaces import ITileEditForm
from plone import api
from plone.app.tiles.browser.edit import DefaultEditForm
from plone.app.tiles.browser.edit import DefaultEditView
from plone.app.tiles.browser.traversal import EditTile
from plone.app.tiles.utils import appendJSONData
from plone.tiles.interfaces import ITileDataManager
from plone.z3cform.interfaces import IDeferSecurityCheck
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserView
from zope.traversing.browser.absoluteurl import absoluteURL


class ICoverTileEditView(IBrowserView):
    """
    """


@implementer(ITileEditForm)
class CustomEditForm(DefaultEditForm):
    """Standard tile edit form, which is wrapped by DefaultEditView (see
    below).

    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """

    def update(self):
        super(CustomEditForm, self).update()

        tile = self.getTile()

        if (not IDeferSecurityCheck.providedBy(self.request) and
                not tile.isAllowedToEdit()):
            # if IDeferSecurityCheck is provided by the request,
            # we're not going to worry about security, perms not set up yet
            raise Unauthorized(
                _(u'You are not allowed to add this kind of tile'))

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        tile = self.getTile()

        # We need to check first for existing content in order not not loose
        # fields that weren't sent with the form
        dataManager = ITileDataManager(tile)
        old_data = dataManager.get()
        for item in data:
            old_data[item] = data[item]
        dataManager.set(old_data)

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

    def getTile(self):
        # if IDeferSecurityCheck is provided by the request,
        # you can't use restricted traverse, perms aren't set up yet.
        if IDeferSecurityCheck.providedBy(self.request):
            view = getMultiAdapter((self.context, self.request),
                                   name=self.tileType.__name__)
            return view[self.tileId]
        else:
            return self.context.restrictedTraverse('@@{0}/{1}'.format(
                self.tileType.__name__, self.tileId,))

    def getContent(self):
        dataManager = ITileDataManager(self.getTile())
        return dataManager.get()


class CustomTileEdit(DefaultEditView):
    """
    Override the default @@edit-tile so we can raise Unauthorized using our
    custom security implementation
    """

    form = CustomEditForm
    index = ViewPageTemplateFile('templates/tileformlayout.pt')

    def __call__(self):
        # We add Cache-Control here because IE9-11 cache XHR GET requests. If
        # you edit a tile, save and re-edit you get the previouw request. IE
        # will list the request as 304 not modified, in its F12 tools, but it
        # is never even requested from the server.
        self.request.response.setHeader('Cache-Control', 'no-cache, must-revalidate')
        return super(CustomTileEdit, self).__call__()


class CoverTileEditView(EditTile):
    """
    Implements the @@edit-tile namespace for our specific tiles, so we can
    check permissions.
    """

    targetInterface = ICoverTileEditView
