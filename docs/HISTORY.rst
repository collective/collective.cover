Changelog
---------

Because you have to know where your towel is.

1.0a2 (2013-04-09)
^^^^^^^^^^^^^^^^^^
- Move Galleria's stylesheet and JS init to <head>. [davilima6]
- New tile: `PloneFormGen`_ embedded form. [ericof]
- New tile: Content Body. [ericof]
- Update package documentation. [hvelarde, jpgimenez]
- Package is now compatible with Plone 4.3. [ericof, jpgimenez, hvelarde]
- Remove dependency on plone.principalsource (closes `#152`_). [ericof]
- Support five.grok 1.3.2 and plone.app.dexterity 2.0.x. [ericof]
- Update JQuery UI to version 1.8.16.9 (fixes `#124`_). [hvelarde]
- Fix TinyMCE table conflict (closes `#142`_). [agnogueira]
- News Items can now be added to the carousel tile (fixes `#146`_).
  [jpgimenez]
- Basic tile date field visibility is now configurable. [jpgimenez]
- Refactor carousel tile to use collective.js.galleria (closes `#123`_).
  [jpgimenez]
- Refactor list tile to use adapters to get the contained items uids.
  [jpgimenez]
- Implements a way to ommit fields from tiles edit form and show it at
  configure form. [jpgimenez]
- Refactor of collection tile. [hvelarde]
- List and carousel tiles now support loading images from folderish content.
  [jpgimenez]
- Have the <base> tag to include a slash at the end so relative ajax calls are
  called for the object and not its parent (fixes `#48`_). [frapell]
- In order to be able to load Dexterity items from the import content GS step,
  we need to provide this interface manualy, until a proper fix in Dexterity
  is implemented. [frapell]
- Make the cover object to be an Item instead of a Container (fixes `#114`_).
  [frapell]
- Date and subjects fields on basic tile are now Read Only (fixes `#129`_).
  [jpgimenez]
- Fix row height in layout view (closes `#128`_). [Quimera]
- Fix filter feature on content chooser (closes `#121`_). [Quimera]


1.0a1 (2013-01-07)
^^^^^^^^^^^^^^^^^^

- Initial release.

.. _`#48`: https://github.com/collective/collective.cover/issues/48
.. _`#114`: https://github.com/collective/collective.cover/issues/114
.. _`#121`: https://github.com/collective/collective.cover/issues/121
.. _`#123`: https://github.com/collective/collective.cover/issues/123
.. _`#124`: https://github.com/collective/collective.cover/issues/124
.. _`#128`: https://github.com/collective/collective.cover/issues/128
.. _`#129`: https://github.com/collective/collective.cover/issues/129
.. _`#142`: https://github.com/collective/collective.cover/issues/142
.. _`#146`: https://github.com/collective/collective.cover/issues/146
.. _`#152`: https://github.com/collective/collective.cover/issues/152
.. _`PloneFormGen`: https://pypi.python.org/pypi/Products.PloneFormGen
