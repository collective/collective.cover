Changelog
---------

There's a frood who really knows where his towel is.

2.2.1 (2019-12-24)
^^^^^^^^^^^^^^^^^^

- Fix multiple regressions caused by the migration of JavaScript code to webpack in release 2.2.0 (fixes `#859 <https://github.com/collective/collective.cover/issues/859>`_, `#861 <https://github.com/collective/collective.cover/issues/861>`_, `#868 <https://github.com/collective/collective.cover/issues/868>`_ and `#871 <https://github.com/collective/collective.cover/issues/871>`_).
  [Mubra]
    

2.2.0 (2019-02-26)
^^^^^^^^^^^^^^^^^^

- Deprecate resource registries; instead, we now use a viewlet in ``plone.htmlhead`` to load JavaScript code.
  This simplifies maintainance of the add-on among multiple Plone versions.
  [rodfersou]

- Process static resources using webpack.
  [rodfersou]


2.1b2 (2018-10-04)
^^^^^^^^^^^^^^^^^^

- Fix behavior of ``remote_url`` field on Basic tiles as populating them from an alternate URL could result on incorrect links stored.
  Remove upgrade step from profile version 22 used to update the field;
  we include a new upgrade step that lists suspicious tiles to help fix any issue by hand (fixes `#839 <https://github.com/collective/collective.cover/issues/839>`_).
  [hvelarde]


2.1b1 (2018-09-28)
^^^^^^^^^^^^^^^^^^

- Fix ``remote_url`` field definition in Banner tile and hide ``a`` tag if no URL is defined.
  [hvelarde]

- Links on Basic tiles are now editable (fixes `#397 <https://github.com/collective/collective.cover/issues/397>`_).
  [hvelarde]

- Avoid ``TypeError`` when a style used on a tile was removed (fixes `#827 <https://github.com/collective/collective.cover/issues/827>`_).
  [rodfersou]

- Avoid ``KeyError`` when tile schema has changed (refs. `brasil.gov.portal#524 <https://github.com/plonegovbr/brasil.gov.portal/issues/524>`_).
  [hvelarde]

- Fix package uninstall.
  [hvelarde]


2.0b1 (2018-08-24)
^^^^^^^^^^^^^^^^^^

.. warning::
    The PFG tile is now deprecated an will be removed in collective.cover 3.
    This version removes the hard dependency on ``plone.app.relationfield``;
    if you're ugrading from a previous version of ``collective.cover`` you must add the extra ``[relations]``.
    Upgrading from versions below 1.2b1 is no longer supported.
    You must upgrade at least to version 1.2b1 before upgrading to this release.

- Update package dependencies.
  [hvelarde]

- Deprecate PFG tile; it will remain available in Plone 4, but not in Plone 5.
  [hvelarde]

- Remove hard dependency on ``plone.app.relationfield``;
  if you're ugrading from a previous version of ``collective.cover`` you must add the extra ``[relations]`` (closes `#684 <https://github.com/collective/collective.cover/issues/684>`_).
  [hvelarde]

- Remove predefined layouts as they were created using Deco grid system and they are broken in Plone 5 (closes `#652 <https://github.com/collective/collective.cover/issues/652>`_).
  You can still create your own layouts using your favorite grid system as usually.
  [rodfersou]

- Remove upgrade steps for old, unsupported releases.
  [hvelarde]

- Remove deprecated adapters ``CollectionUIDsProvider``, ``FolderUIDsProvider`` and ``GenericUIDsProvider``.
  [hvelarde]

- Fix retrieval of available image scales in tile layout configuration for Plone 5 (fixes `#781 <https://github.com/collective/collective.cover/issues/781>`_).
  [rodfersou]

- Fix edit list element in compose tab on Plone 5 (fixes `#770 <https://github.com/collective/collective.cover/issues/770>`_).
  [rodfersou]

- Fix display of tabs in content chooser for Plone 5.
  [cdw9, rodfersou]


1.7b3 (2018-07-09)
^^^^^^^^^^^^^^^^^^

- Review multiple class selection when there are many classes (closes `#785 <https://github.com/collective/collective.cover/issues/785>`_).
  [rodfersou]

- Small code refactor to increase future Python 3 compatibility.
  [hvelarde]


1.7b2 (2018-04-27)
^^^^^^^^^^^^^^^^^^

- Fix multiple CSS class selection in tile configuration for tiles different from basic tile.
  [rodfersou]


1.7b1 (2018-04-27)
^^^^^^^^^^^^^^^^^^

- Update i18n, Brazilian Portuguese and Spanish translations.
  [hvelarde]

- Allow selection of multiple CSS classes in tile configuration.
  [rodfersou]

- Small code refactor to increase future Python 3 compatibility;
  add dependency on `six <https://pypi.python.org/pypi/six>`_.
  [hvelarde]

- Provide alternative text for image fields in tiles (closes `#628 <https://github.com/collective/collective.cover/issues/628>`_).
  [hvelarde]


1.6b5 (2017-11-21)
^^^^^^^^^^^^^^^^^^

- Fix purging of tile annotations when removing tiles from the cover layout.
  This solves exponential growth of cover objects when using versioning,
  leading to check in/check out (plone.app.iterate) timeouts on backends using proxy servers (fixes `#765 <https://github.com/collective/collective.cover/issues/765>`_).
  [rodfersou]

- Do not auto include package dependencies, but declare them explicitly.
  [hvelarde]


1.6b4 (2017-10-30)
^^^^^^^^^^^^^^^^^^

- Revert declaring ``cover_layout`` field in content type schema as ``readonly`` (fixes `#761 <https://github.com/collective/collective.cover/issues/761>`_).
  [hvelarde]


1.6b3 (2017-10-23)
^^^^^^^^^^^^^^^^^^

- Fix edit view of carousel tile when one carousel item has a unicode character in its title (fixes `#757 <https://github.com/collective/collective.cover/issues/757>`_).
  [fulv]

- Explicitly declare ``cover_layout`` field in content type schema as ``readonly``;
  Robot Framework tests pass again with latest version of Plone 4.3 (fixes `#759 <https://github.com/collective/collective.cover/issues/759>`_).
  [hvelarde]


1.6b2 (2017-09-01)
^^^^^^^^^^^^^^^^^^

- Use correct ``image/x-icon`` MIME type for ICO file format (fixes `#750 <https://github.com/collective/collective.cover/issues/750>`_).
  [hvelarde]

- Fix IDatetimeWidget tile override if using plone.app.contenttypes >= 1.1.1:
  collective.z3cform.datetimewidget is merged into plone.formwidget.datetime,
  so the zcml must override the template from plone.formwidget.datetime.z3cform.interfaces.IDatetimeWidget
  as well. (closes `#745`_).
  [idgserpro]

- Review tile refresh using custom event.
  [rodfersou]


1.6b1 (2017-06-23)
^^^^^^^^^^^^^^^^^^

- Fix deprecation of adapters made in previous release, as they were incorrectly removed.
  Code removal will still happen in collective.cover v1.7.
  [idgserpro]

- Use absolute URL for root in content chooser tree (fixes `#733 <https://github.com/collective/collective.cover/issues/733>`_).
  [maurits]

- Fix content chooser clear button to update results (closes `#727`_).
  [rodfersou]

- Drop support for Plone 4.2.
  [hvelarde]

- Fix typo in basic tile template (``is_empty`` is not a property but a function).
  [hvelarde]


1.5b1 (2017-06-12)
^^^^^^^^^^^^^^^^^^

.. Warning::
    If you are upgrading plone.app.tiles note that latests versions of this package no longer depend on plone.app.drafts.
    You should explicitly add plone.app.drafts to the `eggs` part of your buildout configuration to avoid issues.
    You can safely uninstall plone.app.drafts after that, if you are not using it.

    Adapters used to get the items inside a folder or the results of the query in a collection were deprecated.
    The following classes will be removed in collective.cover v1.7: ``ICoverUIDsProvider``, ``CollectionUIDsProvider``, ``FolderUIDsProvider`` and ``GenericUIDsProvider``.

- Information stored on basic tiles populated with private content is no longer shown to users without proper permissions (fixes `#721`_).
  [hvelarde]

- Dropping a folder on a carousel tile no longer populates the tile with the items inside the folder;
  populating the carousel tile with the results of the query in a collection is still supported.
  [rodfersou, hvelarde]

- Dropping a folder or a collection into a list tile previously resulted in the tile being populated with the items inside the folder or the results of the query in the collection,
  making impossible to have folders or collection as items of the list tile themselves (fixes `#713`_).
  [rodfersou, hvelarde]

- Update recommended versions of Blocks dependencies to keep in sync with current Mosaic development.
  [hvelarde]

- Fix order of UUIDs of sorted function in ListTile's 'results' method.
  [idgserpro]

- Review content chooser events to happen just at Compose tab (fixes `#710`_).
  [rodfersou]

- Do not assume all tile types have schemas.
  [alecm]

- Do not declare the ``Cover`` class as an implementer of ``IDAVAware``;
  This makes absolutely no sense and is causing an error when doing a GenericSetup export (fixes `#396`_).
  [hvelarde]


1.4b1 (2016-12-14)
^^^^^^^^^^^^^^^^^^

- Fix ``@@updatetilecontent`` view to avoid rendering outdated data.
  [hvelarde]

- Fix ``TypeError`` when changing default image scale on basic tiles (fixes `#686`_).
  [rodfersou]

- Fixed adding a 'more' link in list tiles.
  Previously you could select an item to use as 'more' link,
  but it did not stick.  [maurits]

- The ``replace_with_objects`` method was removed from the list tile;
  use ``replace_with_uuids`` instead.
  [hvelarde]

- "Add Content" button is now shown also in Plone 5.
  [hvelarde]

- Avoid exceptions while using the content chooser in Plone 5.
  [hvelarde]

- Add helper function to get the human representation of a mime-type on Dexterity-based content types.
  This fixed an ``AttributeError`` that was causing an exception on Plone 5.
  [hvelarde]

- We now get the types that use the view action in listings in Plone 5 also.
  [hvelarde]

- ESI support was refactored; now all tiles inherit from ``ESIPersistentTile`` by default.
  [hvelarde]

- Add plone.protect when save layout (fixes `#651`_).
  [rodfersou]

- Use ``pat-modal`` instead of ``prepOverlay`` for Plone 5 (fixes `#641`_).
  [rodfersou]

- Enforce usage of plone.app.tiles >= 1.1.0 to avoid creation of zillions of empty blob files when using versioning (fixes `#532`_, huge HT @datakurre).
  [hvelarde]


1.3b1 (2016-09-12)
^^^^^^^^^^^^^^^^^^

.. Warning::
    A huge code refactoring was made as part of the removal of the dependency on five.grok.
    The following unused views were removed: ``AddCTWidget``, ``AddTileWidget``, ``SetWidgetMap``, ``UpdateWidget`` and ``RemoveTileWidget``.
    All Compose tab helper views use now ``cmf.ModifyPortalContent`` permission.
    All Layout tab helper views use now ``collective.cover.CanEditLayout`` permission.
    The ``BaseGrid`` class is now located in the ``collective.cover.grids`` module.

- Update Traditional Chinese translation.
  [l34marr]

- Remove dependency on five.grok (closes `#510`_).
  [l34marr, rodfersou]

- Use the `X-Robots-Tag` header to avoid indexing of image scales on default view;
  this will reduce the number of 404 (Not Found) responses generated by crawlers visiting the site in search of volatile content.
  [hvelarde]

- Enforce usage of plone.api >= 1.4.11 to avoid `TypeError` while running upgrade step to profile 14.
  [hvelarde]


1.2b1 (2016-07-04)
^^^^^^^^^^^^^^^^^^

- A new calendar tile was added.
  The tile dislays a calendar that highlights the events taking place on the current month,
  the same way as the standard calendar portlet does.
  [rodfersou]

- Handle `AssertionError` on upgrade step to profile 13 to avoid failures when a cover object has duplicated tiles on it.
  Now, an error message will be logged and the object will be skipped;
  you must manually remove the duplicated tiles (closes #619).
  [hvelarde]


1.1b1 (2016-03-31)
^^^^^^^^^^^^^^^^^^^

.. Warning::
    This release removes some packages from the list of dependencies.
    Be sure to read the whole changelog and apply the related changes to your buildout configuration while upgrading.
    Also, note that we have reorganized the static resources contained here;
    as some of them are not registered in Resource Registry tools, you could end with a broken layout if you don't clear your intermediate caches.

- Enforce usage of plone.app.blocks 2.2.1 to avoid issues with tiles breaking the whole cover page.
  [hvelarde]

- Add option to select random items in collection tile (closes `#608`_).
  [rodfersou]

- Carousel tile now uses a relative ratio to set its height (fixes `#414`_).
  [terapyon, hvelarde]

- Remove hard dependency on plone.app.referenceablebehavior as Archetypes is no longer the default framework in Plone 5.
  Under Plone < 5.0 you should now explicitly add it to the `eggs` part of your buildout configuration to avoid issues while upgrading.
  [hvelarde]

- Link integrity was refactored to work on all tiles and under Plone 5;
  a hard dependency on Products.Archetypes was removed (fixes `#578`_).
  [hvelarde, rodfersou]

- Do not use the calendar tool to discover Event-like objects as it was removed on Plone 5.
  Instead, try to guess if an object is an Event by using its catalog metadata.
  [hvelarde]

- Package is now also tested with plone.app.contenttypes installed;
  a few bugs related with API incompatibilities among Archetypes and Dexterity were fixed.
  [hvelarde]

- Remove Grok dependency for vocabularies.
  [l34marr]

- You can now use a collection to populate a carousel tile;
  search results without a lead image will be bypassed (fixes `#574`_).
  [rodfersou]

- Shows message to user if an exception is thrown in a tile in AJAX calls. (closes `#581`_).
  [idgserpro]

- Fix date format in collection tiles (closes `#584`_).
  [tcurvelo]

- RichText tile no longer breaks with plone.app.widgets installed (closes `#543`_).
  [frapell, rodfersou]

- Add missing dependency on collective.z3cform.datetimewidget.
  [hvelarde]

- Remove hard dependency on plone.app.stagingbehavior as that package is no longer needed in Plone 5.
  Under Plone < 5.0 you should now explicitly add it to the `eggs` part of your buildout configuration to avoid issues while upgrading.
  [hvelarde]

- Implement drag and drop among tiles (closes `#487`_).
  [rodfersou]

- Clean up static files.
  [rodfersou]


Previous entries can be found in the HISTORY.rst file.


.. _`#396`: https://github.com/collective/collective.cover/issues/396
.. _`#414`: https://github.com/collective/collective.cover/issues/414
.. _`#487`: https://github.com/collective/collective.cover/issues/487
.. _`#510`: https://github.com/collective/collective.cover/issues/510
.. _`#532`: https://github.com/collective/collective.cover/issues/532
.. _`#543`: https://github.com/collective/collective.cover/issues/543
.. _`#574`: https://github.com/collective/collective.cover/issues/574
.. _`#578`: https://github.com/collective/collective.cover/issues/578
.. _`#581`: https://github.com/collective/collective.cover/issues/581
.. _`#584`: https://github.com/collective/collective.cover/issues/584
.. _`#608`: https://github.com/collective/collective.cover/issues/608
.. _`#641`: https://github.com/collective/collective.cover/issues/641
.. _`#651`: https://github.com/collective/collective.cover/issues/651
.. _`#686`: https://github.com/collective/collective.cover/issues/686
.. _`#710`: https://github.com/collective/collective.cover/issues/710
.. _`#713`: https://github.com/collective/collective.cover/issues/713
.. _`#721`: https://github.com/collective/collective.cover/issues/721
.. _`#727`: https://github.com/collective/collective.cover/issues/727
.. _`#745`: https://github.com/collective/collective.cover/issues/745
