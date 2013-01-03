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

``collective.cover`` is a package that allows the creation of advanced covers
for websites homepages, especially for news portals, government and intranets
that require more resources than a simple page or collection can offer. However, 
despite offering rich resources to build a cover, ``collective.cover`` also
provides a very easy mechanism for managing it's contents, fully based on drag 
and drop interface.

``collective.cover`` is based on Blocks and Tiles the same as Deco, the new
layout composition system for Plone.

.. TODO: add links to Blocks, Tiles and Deco

.. TODO: add a comparisson among Deco and collective.cover

Use cases
^^^^^^^^^

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


Don't Panic
-----------

Adding Cover
^^^^^^^^^^^^^

.. figure:: https://raw.github.com/collective/collective.cover/master/cover1.png
    :align: center
    :height: 312px
    :width: 367px


To add a cover you should perform the same procedure used to any type of 
content in Plone:

1. Navigate to the folder where you want to create a cover;

2. Click in "Add Item ..." and choose "Cover";

Then, you have to inform some specific data to create the cover:

3. Fill the required fields as explained below:
    - Title: Enter a name of your cover.
    - Description: a informative description of your cover.
    - Layout: Choose one of the predefined layouts.

4. Click in "Save".

Your cover is now created based on the informed data.



Adding content in your Cover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://raw.github.com/collective/collective.cover/master/cover2.png
    :align: center
    :height: 405px
    :width: 706px

After you create your cover, you'll see it comes with some predefined blocks
 (according to the chosen layout), but it still have no associated content. 
To define the content that will appears on your cover perform the following 
steps:

1. Click in the "Compose" tab;

2. Click in the "Add Content" tab on the right of the green bar;

A small window will appears showing the most recent items added in the portal.

3. Click on the title of any choosen item in the list and drag it to one of 
the tiles (dotted boxes) in the content area;

4. Release the item on one of the boxes. Each Tile allows only certain types 
of content to be added. If you the content you choose is allowed the box will 
turn green, if it's not permitted it will remains gray;

.. figure:: https://raw.github.com/collective/collective.cover/master/cover3.png
    :align: center
    :height: 405px
    :width: 706px

The information content will be automatically applied to the selected 
destination tile and that content will be visible on the cover.

5. Repeat for add content in each one of the existing tiles.

6. To visualize the final result click in "View" tab.

Besides using the most recent items you also have two other listing options to 
find the content you want.


Searching Content
++++++++++++++++++

You can use the search field in the selection content window to find the object 
you want.

1. Type the term you want to find;

2. Click in the "Search" button.

The items related to the term you search will be displayed and can be used like 
the steps mentioned above.

Content tree
+++++++++++++

Inside selection content window you can also navigate through your site to locate 
existing content.

1.  Click the "Content Tree" tab;

2. Click on the links to browse through the structure of your site until you find 
the desired content. All items listed are available to be used like the  above 
mentioned steps.

Changing information from a Content
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://raw.github.com/collective/collective.cover/master/cover6.png
    :align: center
    :height: 494px
    :width: 693px

After a content is added to a cover, a copy of the data will be stored in the Cover 
and appear to the end user. If it's necessary, you can edit some data of this content 
exclusively for the cover without changing the information in the original item. This 
feature is very useful to adapt the content for the cover,  making, for example, the 
titles more suitable for display on a homepage. To change the data take the following 
steps.

1. Click on the "Compose" tab;

2. Click on the portion of text you want to change, like the title, description or 
any other text element.

3. Change the text and click "Save."

The changes will be apply to your cover immediately.

*Important:* The changes will be apply only in the cover tile, not in the original 
content.


Advanced Actions
-----------------

Changing the layout of your cover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have created a blank cover or want to change the structure of your current 
cover you can add or delete tiles, change the place of an existing tile or even 
change the rows and columns structure of the cover. All these operations can be 
performed from the "Layout" tab.

.. figure:: https://raw.github.com/collective/collective.cover/master/cover4.png
    :align: center
    :height: 427px
    :width: 696px


A cover is a combination of three basic elements:

   - Lines (which may contain one or more columns)
   - Columns (which may contain one or more tiles)
   - Tiles


Adding rows and columns
++++++++++++++++++++++++

To add a new line you can take the following steps:

1. In the Layout tab, click the Line icon and drag it to your page;

After that you need to add a column to this line so you can add tiles later.

2. Click on the icon column and drag this icon into a column. You can repeat this 
operation as many times as you need. ``collective.cover`` will automatically
divide the space between the rows.

Changing the columns width
++++++++++++++++++++++++++++++

You can control the width of each column individually. Just do the following:

1. Click on the configuration icon of the desired column;

2. Drag the slider to one side or another, adjusting the desired number. The 
higher the number, the higher the column width.

.. figure:: https://raw.github.com/collective/collective.cover/master/cover5.png
    :align: center
    :height: 386px
    :width: 691px


3. Click the Save button.

By default, the cover uses a grid of 16 units. Therefore, the sum of the all widths 
in a columns must not exceed the number 16. To make your management easer, when 
editing the widths always start changing the width of the smaller column.

Adding new tiles
^^^^^^^^^^^^^^^^^^

Now that you have created new columns, you can add new tiles in it. To add a new 
tile, do the following:

1. In the Layout tab, click in the Tile icon and drag it to the column where you 
want to put it;

2. Choose one of the available tiles;

3. Change the configuration as desired;

4. Click the Save button.

Now your new tile can be used in the Compose tab to add contents.

Setting tiles
^^^^^^^^^^^^^^

At any time you can change the settings in the previous item. Just take the 
following steps:

1. In the Layout tab, click the Setup icon of the respective tile;

2. Change the information;

3. Click the Save button.


Moving the tiles
^^^^^^^^^^^^^^^^^

On a page that has more than one column, you can move the places of your 
tiles in a simple and fast way:

1. Click in a tile and drag it to the new column;

2. When you release the tile it will be positioned in the new column;

3. Repeat as often as necessary;

4. When finished, click the the Save button and new configuration will be 
applied.


Saving a layout as a model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can save one of your covers as a template for making other covers in your website. 
Just do the following:

1. Click in the Layout tab;

2. At the top of the page, enter a name for your model;

3. Click the Save button.

Now your layout can be used as a model to create new covers, as explained in 
section "Adding a cover".



Views
^^^^^

Tiles for the collective.cover package provide 3 different views:

Rendered view
+++++++++++++

This is the view that will be rendered for anyone that has view permission.
It will render all fields defined in the schema of the tile, based on their
configuration saved from the configuration view.

Edition view
++++++++++++

This view is a common edit view, where all fields from the schema definition
of the tile will be rendered in an "edit" mode. Data enterd here will persist
in the tile itself.
All fields from the schema will get rendered, no matter their configuration
from the configure view.
This view is accessed through the "Compose" view of the cover. You should see
an "edit" button for each tile.
If you don't want your tile to be able to be editable, you should override
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

The configuration view utilizes z3c.form to be automatically generated based on
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

1. The view will get rendered always, so you need to add conditions to show
   specific content based on what data the tile has, if any.

2. You need to render content based on the tile's fields configurations.
   For that, there's a helper method provided with every tile called
   "get_configured_fields". This will iterate over all fields, and will
   get the configuration and data for each, and also in the order that 
   they should be rendered. If the field has no data stored, then it will 
   not get included in the returned values.
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

Recommendation:: Use the scale saved from the configuration. Check lines 26 through
34 from the collection.pt file under tiles/templates directory to get the idea.


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
    facilitate inheritance. In ``collective.cover`` (this package), we don't
    want to use portlets at all.



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
.. _`81`: https://github.com/collective/collective.cover/issues/81
.. _`112`: https://github.com/collective/collective.cover/issues/112
