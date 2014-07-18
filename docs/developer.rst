Developer documentation
***********************

.. contents:: Table of Contents

Views
^^^^^

Tiles for the collective.cover package provide 3 different views:

Rendered view
+++++++++++++

This is the view that will be rendered for anyone that has View permission. It
will render all fields defined in the schema of the tile, based on their
configuration, as set in the configuration view.

Edit view
+++++++++

This view is a common edit view, where all fields from the schema definition
of the tile will be rendered in an "edit" mode. Data entered here will persist
in the tile itself.

All fields from the schema will get rendered, irrespective of their setting in
the configuration view.

This view is accessed through the "Compose" view of the cover. You should see
an "edit" button for each tile.

If you don't want your tile to be editable, you should override the
``is_editable`` attribute of your tile base class and set it to False

Configuration view
++++++++++++++++++

This view is similar to the edit one, except it is intended for configuring
different aspects of the tile. From here you can specify which fields get
rendered when viewing the tile, or the order in which they show up.

In addition, each field widget can provide specific configuration options.
For instance, an ITextLinesWidget will provide an extra configuration 
option, "HTML tag", which allows to specify the HTML tag to be used when
rendering data saved in this field.

This view is accessed through the "Layout" view of the cover. You should see
a "configuration" button for each tile.

If you don't want your tile to be configurable, you should override the
``is_configurable`` attribute of your tile base class and set it to False

Writing a custom widget in "configure" mode for a field
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The configuration view uses z3c.form to automatically render a form based on
the tile's schema definition. For that, it renders widgets in a "configure" 
mode. You can see how existing ones are defined, checking the configure.zcml
file under tiles/configuration_widgets

How to develop a tile for collective.cover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow instructions in David Glick's `Using tiles to provide more flexible
Plone layouts`_ to understand how to develop tiles, and how they work.

Instead of inheriting from ``zope.interface.Interface``, the tile data
interface class should inherit from
``collective.cover.tile.base.IPersistentCoverTile``

Instead of inheriting from ``plone.tiles.PersistentTile``, the tile
must inherit from ``collective.cover.tile.base.PersistentCoverTile``.

Register your tile on the registry using the "plone.app.tiles" record::

  <?xml version="1.0"?>
  <registry>
    <record name="plone.app.tiles">
      <value purge="false">
        <element>my.package.mytile</element>
      </value>
    </record>
  </registry>

There are a couple of methods defined in this base class that provide
additional functionality expected by the cover object, that you may
need to override in your class, if your use case requires it:

**populate_with_object(obj)**
    It takes a Plone content object as parameter, and it will store the
    content information into the tile. Make sure to call this method to check
    for permissions before adding content to the tile. Check the code of
    existing tiles for examples of use.

**delete()**
    It removes the persistent data created for the tile.

**accepted_ct()**
    It returns a list of valid content types that this tile will accept, or
    ``None`` in case it doesn't accept any.

**get_tile_configuration()**
    It returns the stored configuration options for this tile.

Storage
+++++++

Data and configuration for tiles are stored in an annotation of the context
where the tile is being shown.

You can see how this works by looking into data.py and configuration.py under 
the tiles directory.

Render view
+++++++++++

In order to visualize the tile's content, you need to write a view that will
render it. For that, you need to take a few things into consideration.

#. The view will always be rendered, so you need to add conditions to show
   specific content based on what information the tile has, if any.

#. You need to render content based on the configuration of the tile fields.
   For that, there's a helper method provided with every tile called
   ``get_configured_fields``. This will iterate over all fields, and will
   get the configuration and data for each, in the order that they should be
   rendered. If the field has no data stored, then it will not be included
   among the returned values.

   You can override this, in case you need a different behavior, check
   collection.py under the tiles directory and collection.pt under the
   tiles/templates directory for an example.

#. The tile template **must** include an HTML element with the ``tile-content``
   CSS class name. This way, after configuration or edition, the tile will
   be automatically reloaded via AJAX. If you don't include this, edition
   and configuration will missbehave.
   Here's and example::

    <div class="my-custom-tile tile-content">
         Some really cool stuff just your tile is able to do
    </div>

   Check `this package tile templates to see more examples.`_

For additional hints on how to create a template for your tile and make it
work, check all tiles provided by this package, under the tiles directory.

.. _`this package tile templates to see more examples.`: https://github.com/collective/collective.cover/tree/master/src/collective/cover/tiles/templates

Image field and scales
++++++++++++++++++++++

To add an image field to your tile::

    image = NamedImage(
        title=_(u'Image'),
        required=False,
    )

Then, you have several ways of using image scales in your tile templates.

#. You can pass width and height to the ``scale`` method explicitly::

    <img tal:define="scales view/@@images;
                     thumbnail python: scales.scale('image', width=64, height=64);"
       tal:condition="thumbnail"
       tal:attributes="src thumbnail/url;
                       width thumbnail/width;
                       height thumbnail/height;
                       class position;
                       alt view/data/title" />

#. Or you can use Plone predefined scales::

    <img tal:define="scales view/@@images;
                     thumbnail python: scales.scale('image', scale=scale);"
         tal:condition="thumbnail"
         tal:attributes="src thumbnail/url;
                         width thumbnail/width;
                         height thumbnail/height;
                         class position;
                         alt view/data/title" />

.. Tip::
    Use the scale saved from the configuration. Check tile templates to get
    the idea.

Cover tiles supports external images too, that means than if you drop a
content with an image into a cover tile than implements an image field, cover
will honor the image and scales in the original object. This way the image
data isn't duplicated and products than allow scales modifications are
supported.


.. _`Using tiles to provide more flexible Plone layouts`: http://glicksoftware.com/blog/using-tiles-to-provide-more-flexible-plone-layouts


Grid systems
++++++++++++

By default collective.cover uses a deco 16 column grid.

If your theme provides a css framework with a different grid system
(such as Twitter Bootstrap or Zurb Foundation) you can use that
instead of the default deco grid.  To do so, your theme package should
provide a new grid system class which implements the
collective.cover.interfaces.IGridSystem interface.

#. Implement a grid system::

    from five import grok
    from collective.cover.layout import Deco16Grid

    class Bootstrap3(Deco16Grid):
        grok.name('bootstrap3')
        ncolumns = 12
        title = _(u'Bootstrap 3')

        def columns_formatter(self, columns):
            prefix = 'col-md-'
            for column in columns:
                width = column['data']['column-size'] if 'data' in column else 1
                column['class'] = self.column_class + ' ' + (prefix + str(width))

            return columns

#. Register your new grid system (in configure.zcml) ::

    <utility factory="my.theme.module.Bootstrap3" name="bootstrap3" />

#. Or using grok::

    <grok:grok package="." />


Once registered you can select your grid system on the Cover Settings
panel.

WARNING: Switching the grid system will apply to all new and existing
covers.  If you already made layouts for a 16 column grid and switch to
e.g. a 12 column grid, you will have to manually update all existing
covers (their layout is not recalculated automatically).
