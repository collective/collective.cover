Installation
------------

.. Note::
   ``collective.cover`` has been tested in production with Plone 4.2.x only.

To enable this package in a buildout-based installation:

1. Edit your buildout.cfg and add add the following to it::

    [buildout]
    ...
    eggs =
        collective.cover

    [versions]
    ...
    plone.app.blocks = 1.0
    plone.app.drafts = 1.0a2
    plone.app.jquery = 1.7.2
    plone.app.jquerytools = 1.5.5
    plone.app.tiles = 1.0.1
    plone.tiles = 1.2

2. If you are using Plone 4.2.x you need to add the following also::

    [versions]
    ...
    collective.js.jqueryui = 1.8.16.9

After updating the configuration you need to run ''bin/buildout'', which will
take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ``collective.cover`` and click the 'Activate' button.

Note: You may have to empty your browser cache and save your resource
registries in order to see the effects of the package installation.
