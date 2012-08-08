****************
collective.cover
****************

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

An easy-to-use package to create complex covers for Plone sites. Under
development (`see and comment our mockups online`_).

Government, news sites, and intranets have special requirements on terms of
permissions and versioning.

For instance, suppose you are running The Planet, a news site that has a bunch
of editors focused on getting news on different topics like Economy, Health or
Sports.

If you are the main publisher of the site, you may want to leave people
working on the Economy section to take care of their content published on the
cover, but you don't want that same people messing around the Sports section.

Also, suppose you have the final game of the World Cup and the match is going
to be defined on penalties: you may want to prepare a couple of cover pages
and publish the right one focused on the team that won at the end.

This is the kind of issues we want to solve with this package; we are far from
it, but that is the idea.

Use cases
^^^^^^^^^

- [X] a front page may have different layouts
- [X] layouts are created by a Site Administrator TTW
- [ ] the package will provide some layouts by default
- [X] layouts are made of groups of tiles
- [X] groups of tiles may have different editing permissions
- [X] a Site Administrator can drag&drop tiles and groups of tiles around the
  layout
- [X] some tiles could be configured by Site Administrators (fields shown,
  image location, and so on…)
- [X] a Site Administrator will define which fields will be shown on each tile
- [X] tiles will be associated with different kind of objects: static text
  tiles, content type tiles, collection tiles, portlet tiles, and so on…
- [X] only users with specific permissions can modify the content inside a
  group of tiles
- [X] a user can associate content to a tile using a simple drag&drop metaphor
  (if the content and the tile do match)
- [ ] a user can easily edit the content of a tile in place
- [ ] front page edition will take place on a working copy of the object
- [X] a front page may have versions
- [ ] it will be easy to implement a responsive design for a front page

Alternate solutions
^^^^^^^^^^^^^^^^^^^

Over the years there have been some packages to solve the problem of creating
covers in Plone; we have used and are taking ideas from the following:

`CompositePack`_
    Very old; the legacy code is so complex that is not maintainable anymore.
    It has (arguably) the best user interface of all. Layouts can not be
    created TTW. Viewlets are just page templates associated with content
    types; you can drag&drop viewlets around the layout. Publishers love it.

`CMFContentPanels`_
    Code is very old, but still maintained (at least works in Plone 4). Allows
    to create complex layouts TTW and use any layout as a template. Easy to
    extend and edit (but is terrible to find a content to use). Needs a lot of
    memory to work and aggressive cache settings.

`Collage`_
    It allows to create layouts TTW but it has (arguably) the worst user
    interface of all. It is easily extended and there are several add-ons
    available that provide new functionality for it.

Home Page Editor of the Brazilian Chamber of Deputies Site
    Strongly based on `Collage`_, this package was presented at the `World
    Plone Day 2012 Brasilia`_. It allows the edition of home pages and the
    definition of permissions on blocks of content. Available only for Plone 3
    and not openly published… yet.

`collective.panels`_
    A new package that lets site editors add portlets to a set of new
    locations: above and below page contents, portal top and footer. The
    package comes with a number of flexible layouts that are used to position
    the portlets, and locations can be fixed to the nearest site object, to
    facilitate inheritance. In `collective.cover` (this package), we don't
    want to use portlets at all.

Don't Panic
-----------

How to develop a tile for collective.cover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow instructions in
http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts
to understand how to develop tiles, and how they work.

Instead of inheriting from plone.tiles.PersistentTile, inherit from
collective.cover.tile.base.PersistentCoverTile.

Register your tile on the registry using the "plone.app.tiles" record::

    <record name="plone.app.tiles">
      <value purge="false">
        <element>my.package.mytile</element>
      </value>
    </record>

There are a couple of methods defined in this base class that provide
additional functionality expected by the cover object, that you should
override in your class:

**populate_with_object(obj)**
    It takes a CT object as parameter, and it will store the content into the
    tile.
    Make sure to call PersistentCoverTile's populate_with_object to
    check for permissions before adding content to the tile. Check existing
    tiles on how they do it.

**delete()**
    It removes the persistent data created for the tile.

**accepted_ct()**
    It returns a list of valid CT that this tile will accept, or None in case
    it doesn't accept any.

**get_tile_configuration()**
    It returns the stored configuration options for this tile.

Image field and scales
++++++++++++++++++++++

To add an image field to your tile::

    image = NamedImage(
        title=_(u'Image'),
        required=False,
        )

Then do you have several ways of using image scales in your tile templates.

1. You can pass the ``scale`` method explicit width and height::

     <img tal:define="scales view/@@images;
                      thumbnail python: scales.scale('image', width=64, height=64);"
          tal:condition="thumbnail"
          tal:attributes="src thumbnail/url;
                          width thumbnail/width;
                          height thumbnail/height" />

2. Or you can use Plone predefined scales::

     <img tal:define="scales view/@@images;
                      thumbnail python: scales.scale('image', scale='mini');"
          tal:condition="thumbnail"
          tal:attributes="src thumbnail/url;
                          width thumbnail/width;
                          height thumbnail/height" />

Mostly Harmless
---------------

.. image:: https://secure.travis-ci.org/collective/collective.cover.png
    :target: http://travis-ci.org/collective/collective.cover

Have an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`see and comment our mockups online`: https://simples.mybalsamiq.com/projects/capas/grid
.. _`CompositePack`: http://plone.org/products/compositepack
.. _`CMFContentPanels`: http://plone.org/products/cmfcontentpanels
.. _`Collage`: http://plone.org/products/collage
.. _`World Plone Day 2012 Brasilia`: http://colab.interlegis.leg.br/wiki/WorldPloneDay
.. _`collective.panels`: https://github.com/collective/collective.panels
.. _`opening a support ticket`: https://github.com/collective/collective.cover/issues

