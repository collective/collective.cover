# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.cover.tiles.list import ListTile, IListTile


class ICarouselTile(IListTile):
    """
    """


class CarouselTile(ListTile):
    index = ViewPageTemplateFile("templates/carousel.pt")
    is_configurable = False
    is_editable = False
