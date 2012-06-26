# -*- coding: utf-8 -*-

# Basic implementation taken from
# http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts

from zope.component import getMultiAdapter
from zope.component import queryUtility

from zope.interface import implements
from zope.interface import Interface

from zope.schema import getFieldsInOrder

from plone import tiles

from plone.app.textfield.interfaces import ITransformer
from plone.app.textfield.value import RichTextValue

from plone.tiles.interfaces import ITileType

from plone.tiles.interfaces import ITileDataManager

from Products.CMFCore.utils import getToolByName

from collective.composition.tiles.configuration import ITilesConfigurationScreen

from collective.composition.tiles.permissions import ITilesPermissions


class IPersistentCompositionTile(Interface):
    """
    Base interface for tiles that go into the composition object
    """

    def populate_with_object(obj):
        """
        This method will take a CT object as parameter, and it will store the
        content into the tile. Each tile should implement its own method.
        """

    def delete():
        """
        This method removes the persistent data created for this tile
        """

    def accepted_ct():
        """
        This method returns a list of valid CT that this tile will accept, or
        None if not
        """

    def get_tile_configuration():
        """
        A method that will return the configuration options for this tile
        """

    def get_configured_fields():
        """
        This method will return all fields that should be rendered and it will
        include specific configuration if any.
        Bear in mind, that in some specific cases, a visibility value can be
        off, and in that case, fields will not be included in the returned
        dictionary from this method
        """

    def setAllowedGroupsForEdit(groups):
        """
        This method assigns the groups that have edit permission to the tile
        """

    def getAllowedGroupsForEdit():
        """
        This method will return a list of groups that are allowed to edit the
        contents of this tile
        """

    def isAllowedToEdit(user):
        """
        This method returns true if the given user is allowed to edit the
        contents of the tile based on which group is he member of.
        If no user is provided, it will check on the authenticated member.
        """


class PersistentCompositionTile(tiles.PersistentTile):

    implements(IPersistentCompositionTile)

    is_configurable = False

    def populate_with_object(self, obj):
        raise NotImplemented

    def delete(self):
        data_mgr = ITileDataManager(self)
        data_mgr.delete()

    def accepted_ct(self):
        valid_ct = None
        return valid_ct

    def get_tile_configuration(self):
        tile_conf_adapter = getMultiAdapter((self.context, self.request, self),
                                             ITilesConfigurationScreen)

        configuration = tile_conf_adapter.get_configuration()

        return configuration

    def get_configured_fields(self):
        tileType = queryUtility(ITileType, name=self.__name__)
        conf = self.get_tile_configuration()

        fields = getFieldsInOrder(tileType.schema)

        results = []

        for name, obj in fields:
            if not self.data[name]:
                # If there's no data for this field, ignore it
                continue

            if isinstance(self.data[name],RichTextValue):
                transformer = ITransformer(self.context, None)
                if transformer is not None:
                    content = transformer(self.data[name], 'text/x-html-safe')
            else:
                content = self.data[name]

            field = {'id': name,
                     'content': content}
            if name in conf:
                field_conf = conf[name]
                if ('visibility' in field_conf and
                    field_conf['visibility'] == u'off'):
                    # If the field was configured to be invisible, then just
                    # ignore it
                    continue

                if 'htmltag' in field_conf:
                    # If this field has the capability to change its html tag
                    # render, save it here
                    field['htmltag'] = field_conf['htmltag']

            results.append(field)

        return results

    def setAllowedGroupsForEdit(self, groups):
        permissions = getMultiAdapter((self.context, self.request, self),
                                      ITilesPermissions)
        permissions.set_allowed_edit(groups)

    def getAllowedGroupsForEdit(self):
        permissions = getMultiAdapter((self.context, self.request, self),
                                      ITilesPermissions)
        groups = permissions.get_allowed_edit()

        return groups

    def isAllowedToEdit(self, user=None):
        allowed = True

        pm = getToolByName(self.context, 'portal_membership')

        if user:
            if isinstance(user, basestring):
                user = pm.getMemberById(user)
        else:
            user = pm.getAuthenticatedMember()

        user_roles = user.getRoles()
        groups = self.getAllowedGroupsForEdit()

        if groups and 'Manager' not in user_roles:
            if not set(user.getGroups()).intersection(set(groups)):
                allowed = False

        return allowed
