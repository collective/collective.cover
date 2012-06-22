**********************
collective.composition
**********************

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

`Cafecito Sprint`_ is taking place right now in São Paulo to release a package
to create front pages for sites running Plone 4.2 and above. Intended audience
is mainly news sites and intranets.

You can `see and comment our mockups online`_. `Join us on IRC`_.

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
    Very old, but still maintained.

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

Don't Panic
-----------

TBA.

Mostly Harmless
---------------

Have an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`Cafecito Sprint`: https://plone.org/events/community/cafecito-sprint
.. _`see and comment our mockups online`: https://simples.mybalsamiq.com/projects/capas/grid
.. _`Join us on IRC`: irc://irc.freenode.net/cafecitosprint
.. _`CompositePack`: http://plone.org/products/compositepack
.. _`CMFContentPanels`: http://plone.org/products/cmfcontentpanels
.. _`Collage`: http://plone.org/products/collage
.. _`Carlos de la Guardia`: https://github.com/cguardia
.. _`opening a support ticket`: https://github.com/collective/collective.composition/issues

