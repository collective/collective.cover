# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema
from zope.component import queryUtility
from plone.app.textfield.interfaces import ITransformer

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.namedfile.field import NamedImage

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.list import ListTile, IListTile


class ICarouselTile(IListTile):
    """
    """

class CarouselTile(ListTile):
    index = ViewPageTemplateFile("templates/carousel.pt")
    is_configurable = False