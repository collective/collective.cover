****************
collective.cover
****************

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

``collective.cover`` is a package that allows the creation of elaborate covers
for website homepages, especially for news portals, government sites and
intranets that require more resources than a simple page or collection can
offer. However, despite offering rich resources to build a cover,
``collective.cover`` also provides a very easy mechanism for managing its
contents, built around a drag-and-drop interface.

``collective.cover`` is based on `Blocks <https://pypi.python.org/pypi/plone.app.blocks>`_ and `Tiles <https://pypi.python.org/pypi/plone.app.tiles>`_,
like `Mosaic <https://pypi.python.org/pypi/plone.app.mosaic>`_,
the new layout solution for Plone.

Demo
^^^^

For impatient types, there is a demo installation of collective.cover on `Heroku <http://collective-cover.herokuapp.com>`_.
It needs about 60 seconds to spin up and it will purge all changes after about an hour of non-usage.

Use cases
^^^^^^^^^

Suppose you are running The Planet, a news portal that has a bunch of editors
focused on getting news on different topics, like Economy, Health or Sports.

If you are the main publisher of the site, you may want to delegate the
construction of the front page of the Economy section to the people working on
that content area, but you might not want them messing around the Sports
section as well.

Also, suppose you have the final game of the World Cup and the match is going
to be defined on penalties: you may want to prepare a couple of cover pages
and publish the right one focused on the team that won in the end.

These are the kind of issues we want to solve with this package; we are still
far from it, but that is the idea.

Who is using it?
^^^^^^^^^^^^^^^^

These are some of the sites using ``collective.cover``:

* `CartaCapital <http://www.cartacapital.com.br/>`_ (BR)
* `Clean Clothes Campaign <http://www.cleanclothes.org/>`_ (NL)
* `Conselho Federal de Administração <http://www.cfa.org.br/>`_ (BR)
* `La Jornada <http://www.jornada.unam.mx/ultimas>`_ (MX)
* `Palácio do Planalto <http://www.planalto.gov.br/>`_ (BR)
* `Portal Brasil <http://www.brasil.gov.br/>`_ (BR)
* `Rede Brasil Atual <http://www.redebrasilatual.com.br/>`_ (BR)
* `Venezolana de Televisión <http://www.vtv.gov.ve/>`_ (VE)

.. figure:: https://raw.github.com/collective/collective.cover/master/cover.png
    :align: center
    :height: 640px
    :width: 490px
    :target: http://www.planalto.gov.br/

    The Presidency of Brazil uses ``collective.cover`` on the front page of its site.

Mostly Harmless
---------------

.. image:: http://img.shields.io/pypi/v/collective.cover.svg
   :target: https://pypi.python.org/pypi/collective.cover

.. image:: https://img.shields.io/travis/collective/collective.cover/master.svg
    :target: http://travis-ci.org/collective/collective.cover

.. image:: https://badge.waffle.io/collective/collective.cover.png?label=ready&title=Ready
    :target: https://waffle.io/collective/collective.cover

.. image:: https://img.shields.io/coveralls/collective/collective.cover/master.svg
    :target: https://coveralls.io/r/collective/collective.cover

Got an idea? Found a bug? Let us know by `opening a support ticket <https://github.com/collective/collective.cover/issues>`_.

Known issues
^^^^^^^^^^^^

* `Versioning creates zillions of empty blob files <https://github.com/collective/collective.cover/issues/532>`_.
  If you're using this feature in your site you have to take special attention to the number of free inodes in your file system,
  as you can run out of them;
  use the ``df -i`` command to check it.

* `Package is not compatible with standard Plone tiles <https://github.com/collective/collective.cover/issues/81>`_.
  This will be addressed in a future release, if we get an sponsor.

See the `complete list of bugs on GitHub <https://github.com/collective/collective.cover/issues?labels=bug&milestone=&page=1&state=open>`_.

Don't Panic
-----------

We are currently working on the documentation of the package; this is what we have right now (contributions are always welcomed):

* `Quick Tour video on YouTube <https://www.youtube.com/watch?v=h_rsSL1e4i4>`_.
* `End user documentation <https://github.com/collective/collective.cover/blob/master/docs/end-user.rst>`_
* `Developer documentation <https://github.com/collective/collective.cover/blob/master/docs/developer.rst>`_

Installation
^^^^^^^^^^^^

To enable this package in a buildout-based installation:

Edit your buildout.cfg and add add the following to it:

.. code-block:: ini

    [buildout]
    ...
    eggs =
        collective.cover

    [versions]
    ...
    collective.js.bootstrap = 2.3.1.1
    plone.app.blocks = 2.2.1
    plone.app.tiles = 1.0.2
    plone.tiles = 1.5.2

If you are using Plone 4.2.x you need to add the following also:

.. code-block:: ini

    [versions]
    collective.js.jqueryui = 1.8.16.9
    plone.app.jquery = 1.7.2
    plone.app.jquerytools = 1.5.7
    plone.app.z3cform = 0.6.3
    plone.directives.form = 1.1

If you want to use a newer release of ``collective.js.bootstrap``, you will need to update ``plone.app.jquery``:

.. code-block:: ini

    [versions]
    plone.app.jquery = 1.8.3

After updating the configuration you need to run ''bin/buildout'', which will
take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ``collective.cover`` and click the 'Activate' button.

.. Note::
    You may have to empty your browser cache and save your resource registries
    in order to see the effects of the product installation.

Not entirely unlike
-------------------

Over the years there have been some packages designed to solve the problem of
creating section covers in Plone. We have used and have taken ideas from the
following:

`CompositePack <https://pypi.python.org/pypi/Products.CompositePack>`_
    Very old; the legacy code is so complex that is not maintainable anymore.
    It has (arguably) the best user interface of all. Layouts can not be
    created TTW. Viewlets are just page templates associated with content
    types; you can drag&drop viewlets around the layout. Publishers love it.

`CMFContentPanels <https://pypi.python.org/pypi/Products.CMFContentPanels>`_
    Code is very old, but still maintained (at least works in Plone 4). Allows
    to create complex layouts TTW and use any layout as a template. Easy to
    extend and edit (but is terrible to find a content to use). Needs a lot of
    memory to work and aggressive cache settings.

`Collage <https://pypi.python.org/pypi/Products.Collage>`_
    Allows the creation of layouts TTW but it has (arguably) the worst user
    interface of all. It is easily extended and there are several add-ons
    available that provide new functionality for it.

`Home Page Editor of the Brazilian Chamber of Deputies Site <https://colab.interlegis.leg.br/browser/publico/camara.home>`_
    Strongly based on `Collage`_, this package was presented at the `World Plone Day 2012 Brasilia <http://colab.interlegis.leg.br/wiki/WorldPloneDay>`_.
    It allows editing of home pages and the definition of permissions on blocks of content.
    Works under Plone 3 only.

`collective.panels <https://pypi.python.org/pypi/collective.panels>`_
    A new package that lets site editors add portlets to a set of new
    locations: above and below page contents, portal top and footer. The
    package comes with a number of flexible layouts that are used to position
    the portlets, and locations can be fixed to the nearest site object, to
    facilitate inheritance. In ``collective.cover`` (this package), we don't
    want to use portlets at all.
