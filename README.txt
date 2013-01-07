****************
collective.cover
****************

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

.. Warning::
   ``collective.cover`` is currently not compatible with standard Plone tiles;
   this will be addressed in a future realease of the package. See `81`_ and
   `112`_ for more information.

``collective.cover`` is a package that allows the creation of elaborate covers
for website homepages, especially for news portals, government sites and intranets
that require more resources than a simple page or collection can offer. However,
despite offering rich resources to build a cover, ``collective.cover`` also
provides a very easy mechanism for managing its contents, built around a
drag-and-drop interface.

``collective.cover`` is based on `Blocks`_ and `Tiles`_, like `Deco`_, the new
layout composition system for Plone.

.. TODO: explain why we need cover instead of just using Deco itself.

.. TODO: add a comparison between Deco and collective.cover

Use cases
^^^^^^^^^

Suppose you are running The Planet, a news site that has a bunch
of editors focused on getting news on different topics, like Economy, Health or
Sports.

If you are the main publisher of the site, you may want to delegate the
construction of the cover page of the Economy section to the people working
on that section content, but you might not want them messing around the
Sports section as well.

Also, suppose you have the final game of the World Cup and the match is going
to be defined on penalties: you may want to prepare a couple of cover pages
and publish the right one focused on the team that won in the end.

These are the kind of issues we want to solve with this package; we are still
far from it, but that is the idea.


Don't Panic
-----------

Adding Cover
^^^^^^^^^^^^^

.. figure:: https://raw.github.com/collective/collective.cover/master/cover1.png
    :align: center
    :height: 312px
    :width: 367px


You add a cover like you would any type of content in Plone:

1. Navigate to the folder where you want to create a cover;

2. Open the "Add Item ..." menu and choose "Cover";

3. Fill in the required fields:
    - "Title" and "Description": Same as with other Plone content, like Page.
    - "Layout": Choose one of the predefined cover layouts.

4. "Save".

Your cover is now created based on the information provided.

Adding content in your Cover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://raw.github.com/collective/collective.cover/master/cover2.png
    :align: center
    :height: 405px
    :width: 706px

After the cover is created, you'll notice it comes with some predefined blocks
(according to the selected layout), but it still has no content associated.
To define the content that will appear on the cover, perform the following
steps:

1. Select the "Compose" tab;

2. Open the "Add Content" tab to the right of the green bar;

A small window will appears showing the most recent items added in the portal.

3. Select the title of any item in the list and drag it to one of
the tiles (dotted boxes) in the content area;

4. Hover the item over one of the Tile boxes. Each Tile allows only certain
types of content to be added. If the content you selected is allowed on that
Tile, the box will turn green. If not, it will remain gray;

5. Release the item.

.. figure:: https://raw.github.com/collective/collective.cover/master/cover3.png
    :align: center
    :height: 405px
    :width: 706px

Information from that content will be automatically applied to the chosen
tile and will be visible on the cover.

5. Repeat the process to add content to each one of the other tiles.

6. To visualize the final result, select the "View" tab.

There are also two other navigation options to find content:


Searching Content
++++++++++++++++++

You can use the search field in the content selection window to locate the
content you want:

1. Type the term you want to find;

2. Push the "Search" button.

The items related to the term you search will be displayed and can be used
according to the steps above.

Content tree
+++++++++++++

Inside the content selection window you can also navigate through your site to
locate existing content.

1. Select the "Content Tree" tab;

2. Select the links to browse through the structure of your site until you find
the desired content. All items listed are available to be used according to the
steps above.

Changing information from a Content
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://raw.github.com/collective/collective.cover/master/cover6.png
    :align: center
    :height: 494px
    :width: 693px

After a content is added to a cover tile, a copy of some of its information will be stored in the cover
and will appear to the end user. If necessary, you can change some of the information related to the content
exclusively for the cover, without changing the information in the original item. This
feature is very useful to adjust the content for the cover. For example, you can shorten
a title to better fit it into a homepage layout.

To change the information on the cover, follow these steps:

1. Select the "Compose" tab;

2. Select the portion of text you want to change, like the title, the description or
any other text element.

3. Change the text and "Save".

The changes will be applied to your cover immediately.

*Important:* As mentioned before, the changes will be applied only to the cover tile, not to the original
content.


Advanced Actions
-----------------

Changing the layout of your cover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have created a blank cover or if want to change the structure of your
current cover, you can add or delete tiles, change the position of an existing
tile, or even change the rows and columns structure of the cover. These
operations can be performed from the "Layout" tab.

.. figure:: https://raw.github.com/collective/collective.cover/master/cover4.png
    :align: center
    :height: 427px
    :width: 696px


A cover is a combination of three basic elements:

   - Rows (which may contain one or more columns, arranged horizontally)
   - Columns (which may contain one or more tiles arranged vertically)
   - Tiles


Adding rows and columns
++++++++++++++++++++++++

To add a new row, follow these steps:

1. In the Layout tab, click the Row icon and drag it to your page;

Then you need to add one or more columns to this row so you can add tiles later:

2. Click on the Column icon and drag it into a row.

You can repeat this operation as often as you need. ``collective.cover`` will
divide the space between the rows and columns automatically.

Changing the width of columns
++++++++++++++++++++++++++++++

You can control the width of each column individually:

1. Push the configuration icon of the desired column;

2. Drag the slider sideways, adjusting the desired number of column widths. The
higher the number, the larger the column width.

.. figure:: https://raw.github.com/collective/collective.cover/master/cover5.png
    :align: center
    :height: 386px
    :width: 691px


3. "Save".

By default, the cover uses a grid of 16 units. Therefore, the sum of the all widths 
in a column must not exceed 16. To make it easier to edit the width of all
columns, adjust first the width of the smallest column.

Adding new tiles
^^^^^^^^^^^^^^^^^^

Now that you have created columns, you can add tiles to it:

1. In the Layout tab, select the Tile icon and drag it to the column where
you want to place it;

2. Choose one of the available tiles in the pop-up overlay;

3. Change the configuration as desired;

4. Push "Save".

The new tile can be used in the Compose tab to select/add content.

Adjusting tiles
^^^^^^^^^^^^^^^

You can change the settings from previously added tiles at any time:

1. In the Layout tab, select the Setup icon of the respective tile;

2. Modify the information;

3. "Save".


Moving tiles around
^^^^^^^^^^^^^^^^^^^^^

On a page that has more than one column, you can conveniently move your tiles
around:

1. Select the "Layout" tab;

2. Click on a tile and drag it over another column in any of the rows;

3. When you release, the tile it will be positioned in the new column;

4. Repeat as often as necessary;

5. When finished, push "Save" and the new configuration will be applied.


Saving a layout as a model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can save one of your covers as a template for creating other covers on your
website: 

1. Select the Layout tab;

2. At the top of the page, enter a name for your model;

3. "Save".

Now this layout can be used as a model to create new covers, as explained in the
section "Adding a cover".



Views
^^^^^

Tiles for the collective.cover package provide 3 different views:

Rendered view
+++++++++++++

This is the view that will be rendered for anyone that has View permission.
It will render all fields defined in the schema of the tile, based on their
configuration, as set in the configuration view.

Edit view
++++++++++++

This view is a common edit view, where all fields from the schema definition
of the tile will be rendered in an "edit" mode. Data entered here will persist
in the tile itself.
All fields from the schema will get rendered, irrespective of their setting in
the configuration view.
This view is accessed through the "Compose" view of the cover. You should see
an "edit" button for each tile.
If you don't want your tile to be editable, you should override
the "is_editable" attribute of your tile base class and set it to False

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
If you don't want your tile to be configurable, you should override
the "is_configurable" attribute of your tile base class and set it to False


Writing a custom widget in "configure" mode for a field
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The configuration view uses z3c.form to automatically render a form based on
the tile's schema definition. For that, it renders widgets in a "configure" 
mode. You can see how existing ones are defined, checking the configure.zcml
file under tiles/configuration_widgets


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
    It takes a Plone content object as parameter, and it will store the content
    information into the tile.
    Make sure to call this method to check for permissions before adding
    content to the tile. Check the code of existing tiles for examples of use.

**delete()**
    It removes the persistent data created for the tile.

**accepted_ct()**
    It returns a list of valid content types that this tile will accept, or None in case
    it doesn't accept any.

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
render it. For that, you need to get some things into consideration.

1. The view will always be rendered, so you need to add conditions to show
   specific content based on what information the tile has, if any.

2. You need to render content based on the configuration of the tile fields.
   For that, there's a helper method provided with every tile called
   "get_configured_fields". This will iterate over all fields, and will
   get the configuration and data for each, in the order that
   they should be rendered. If the field has no data stored, then it will
   not be included among the returned values.
   You can override this, in case you need a different behavior, check
   collection.py under the tiles directory and collection.pt under the
   tiles/templates directory for an example. 

For additional hints on how to create a template for your tile and make it
work, check all tiles provided by this package, under the tiles directory.

Image field and scales
++++++++++++++++++++++

To add an image field to your tile::

    image = NamedImage(
        title=_(u'Image'),
        required=False,
        )

Then, you have several ways of using image scales in your tile templates.

1. You can pass width and height to the ``scale`` method explicitly::

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

Recommendation:: Use the scale saved from the configuration. Check lines 26 through
34 from the collection.pt file under tiles/templates directory to get the idea.


Alternate solutions
^^^^^^^^^^^^^^^^^^^

Over the years there have been some packages designed to solve the problem of creating
section covers in Plone. We have used, and are taking ideas from, the
following:

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
    Allows the creation of layouts TTW but it has (arguably) the worst user
    interface of all. It is easily extended and there are several add-ons
    available that provide new functionality for it.

Home Page Editor of the Brazilian Chamber of Deputies Site
    Strongly based on `Collage`_, this package was presented at the `World
    Plone Day 2012 Brasilia`_. It allows editing of home pages and the
    definition of permissions on blocks of content. Available only for Plone 3
    and not openly published… yet.

`collective.panels`_
    A new package that lets site editors add portlets to a set of new
    locations: above and below page contents, portal top and footer. The
    package comes with a number of flexible layouts that are used to position
    the portlets, and locations can be fixed to the nearest site object, to
    facilitate inheritance. In ``collective.cover`` (this package), we don't
    want to use portlets at all.



Mostly Harmless
---------------

.. image:: https://secure.travis-ci.org/collective/collective.cover.png
    :target: http://travis-ci.org/collective/collective.cover

Got an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`see and comment on our mockups online`: https://simples.mybalsamiq.com/projects/capas/grid
.. _`CompositePack`: http://plone.org/products/compositepack
.. _`CMFContentPanels`: http://plone.org/products/cmfcontentpanels
.. _`Collage`: http://plone.org/products/collage
.. _`World Plone Day 2012 Brasilia`: http://colab.interlegis.leg.br/wiki/WorldPloneDay
.. _`collective.panels`: https://github.com/collective/collective.panels
.. _`opening a support ticket`: https://github.com/collective/collective.cover/issues
.. _`81`: https://github.com/collective/collective.cover/issues/81
.. _`112`: https://github.com/collective/collective.cover/issues/112
.. _`Blocks`: https://github.com/plone/plone.app.blocks
.. _`Deco`: https://github.com/plone/plone.app.deco
.. _`Tiles`: https://github.com/plone/plone.app.tiles
