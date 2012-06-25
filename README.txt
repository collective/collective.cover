**********************
collective.composition
**********************

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

`Cafecito Sprint`_ is taking place right now in São Paulo to release an
easy-to-use Plone package to create front pages. Intended audience is mainly
news sites and intranets.

You can `see and comment our mockups online`_. You can also `join us on IRC`_.

We want to solve the following use cases:

- a front page may have different layouts
- layouts are created by a Site Administrator TTW
- the package will provide some layouts by default
- layouts are made of groups of tiles
- groups of tiles may have different editing permissions
- a Site Administrator can drag&drop tiles and groups of tiles around the
  layout
- some tiles could be configured by Site Administrators (fields shown, image
  location, and so on…)
- a Site Administrator will define which fields will be shown on each tile
- tiles will be associated with different kind of objects: static text tiles,
  content type tiles, collection tiles, portlet tiles, and so on…
- only users with specific permissions can modify the content inside a group
  of tiles
- a user can associate content to a tile using a simple drag&drop metaphor (if
  the content and the tile do match)
- a user can easily edit the content of a tile in place
- front page edition will take place on a working copy of the object
- a front page may have versions
- it will be easy to implement a responsive design for a front page

Over the years there have been some packages to solve the problem of creating
front pages in Plone; we have used and are taking ideas from the following:

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

collective.composition
    This package. Some months ago `Carlos de la Guardia`_ was comisioned to
    update `CompositePack`_ and make it run on Plone 4. He succeeded, but the
    package proved to be hard to maintain and no further features could be
    added. Carlos then started collective.composition implementing the best
    ideas of `CompositePack`_ using new technologies like Dexterity. We ran
    out of money and the work stopped for many months. Now the picture is
    completely different and many things have become clearer. We are using
    some of the code, but we are going to replace old concepts with new ones.

`collective.panels`_
    A new package that tries to solve a similar problem on a different way
    using portlets. We don't want to use portlets at all.

Don't Panic
-----------

TBA.

How to develop a tile for collective.composition
------------------------------------------------

Follow instructions in
http://davisagli.com/blog/using-tiles-to-provide-more-flexible-plone-layouts
to understand how to develop tiles, and how they work.

Instead of inheriting from plone.tiles.PersistentTile, inherit from
collective.composition.tile.base.PersistentCompositionTile.

There are a couple of methods defined in this base class that provide
additional functionality expected by the composition object, that you should
override in your class:

populate_with_object(obj)
    It takes a CT object as parameter, and it will store the content into the
    tile.

delete()
    It removes the persistent data created for the tile.

accepted_ct()
    It returns a list of valid CT that this tile will accept, or None in case
    it doesn't accept any.

get_tile_configuration()
    It returns the stored configuration options for this tile.

Mostly Harmless
---------------

Have an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`Cafecito Sprint`: https://plone.org/events/community/cafecito-sprint
.. _`see and comment our mockups online`: https://simples.mybalsamiq.com/projects/capas/grid
.. _`join us on IRC`: irc://irc.freenode.net/cafecitosprint
.. _`CompositePack`: http://plone.org/products/compositepack
.. _`CMFContentPanels`: http://plone.org/products/cmfcontentpanels
.. _`Collage`: http://plone.org/products/collage
.. _`collective.panels`: https://github.com/collective/collective.panels
.. _`Carlos de la Guardia`: https://github.com/cguardia
.. _`opening a support ticket`: https://github.com/collective/collective.composition/issues

