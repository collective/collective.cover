# -*- coding: utf-8 -*-
from collective.cover import _
from collective.cover.interfaces import IGridSystem
from zope.interface import implementer


class BaseGrid(object):

    """Base class for grid systems."""

    title = u''
    ncolumns = 0

    row_class = 'row'
    column_class = 'column'

    def transform(self, layout):
        for element in layout:
            if 'type' in element:
                if element['type'] == 'row':
                    element['class'] = self.row_class
                    if 'css-class' in element:
                        element['class'] += ' {0}'.format(
                            element['css-class']
                        )
                    if 'children' in element:
                        self.transform(self.columns_formatter(element['children']))
                if element['type'] == 'group' and 'children' in element:
                    self.transform(element['children'])

                if element['type'] == 'tile':
                    element['class'] = 'tile'

    def columns_formatter(self, columns):
        raise Exception('Must be implemented in the child')


@implementer(IGridSystem)
class Bootstrap3(BaseGrid):

    """Bootstrap 3 grid system (12 columns)."""

    ncolumns = 12
    title = _(u'Bootstrap 3')

    def columns_formatter(self, columns):
        prefix = 'col-md-'
        for column in columns:
            width = column.get('column-size', 1)
            column['class'] = self.column_class + ' ' + (prefix + str(width))
            if 'css-class' in column:
                column['class'] += ' {0}'.format(
                    column['css-class']
                )

        return columns


@implementer(IGridSystem)
class Bootstrap2(BaseGrid):

    """Bootstrap 2 grid system (12 columns)."""

    ncolumns = 12
    title = _(u'Bootstrap 2')

    def columns_formatter(self, columns):
        prefix = 'span'
        for column in columns:
            width = column.get('column-size', 1)
            column['class'] = self.column_class + ' ' + (prefix + str(width))
            if 'css-class' in column:
                column['class'] += ' {0}'.format(
                    column['css-class']
                )

        return columns


@implementer(IGridSystem)
class Deco16Grid(BaseGrid):

    """Deco grid system (16 columns)."""

    title = _(u'Deco (16 columns)')
    ncolumns = 16
    column_class = 'cell'

    def columns_formatter(self, columns):
        w = 'width-'
        p = 'position-'
        offset = 0
        for column in columns:
            width = column.get('column-size', 1)
            column['class'] = self.column_class + ' ' + (w + str(width)) + ' ' + (p + str(offset))
            if 'css-class' in column:
                column['class'] += ' {0}'.format(
                    column['css-class']
                )
            offset = offset + width
        return columns
