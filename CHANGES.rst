Changelog
---------

There's a frood who really knows where his towel is.

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


.. _`#414`: https://github.com/collective/collective.cover/issues/414
.. _`#487`: https://github.com/collective/collective.cover/issues/487
.. _`#543`: https://github.com/collective/collective.cover/issues/543
.. _`#574`: https://github.com/collective/collective.cover/issues/574
.. _`#578`: https://github.com/collective/collective.cover/issues/578
.. _`#581`: https://github.com/collective/collective.cover/issues/581
.. _`#584`: https://github.com/collective/collective.cover/issues/584
.. _`#608`: https://github.com/collective/collective.cover/issues/608
