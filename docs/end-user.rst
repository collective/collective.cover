**********************
End user documentation
**********************

.. contents:: Table of Contents

Basic concepts
--------------

Tiles
^^^^^

Tiles are blocks of content used to compose pages. A standard installation of
collective.cover includes the following tiles:

Banner
++++++

A Banner tile shows an image or heading text pointing to a link; Banner tile
fields include title, an image and a URL.

You can drop any object into a Banner tile. Fields in the tile will be
populated with the object metadata. All fields are user-editable and you can
even upload a different image into the tile if you want.

Basic
+++++

A Basic tile shows almost all metadata of an object; it includes its title,
description, date, tags and an image, if the object has one.

You can drop any object into a Basic tile. Fields in the tile will be
populated with the object metadata. All fields are user-editable (except for
date and tags) and you can even upload a different image into the tile if you
want. The title and image fields will include a link to the original object
location.

Carousel
++++++++

A Carousel tile shows a slideshow made with a list of individual items; every
item will show an image, title and description. Carousel tiles are 100%
responsive, support native-like swipe movements and use hardware optimized
animations.

You can drop any object in a Carousel tile. Right now, you can not edit
individual items metadata in the carousel, but you can remove or reorder them.
You can also specify if the carousel will start playing the slideshow
automatically or not. Every item in the slideshow will have a link pointing
back to the original object.

Carousel tile is fully responsive, so be sure to configure it to use the image size that fits better the maximum desired size.

Collection
++++++++++

A Collection tile shows a list of items resulting from a 'Collection'; every
item will show its title, description, date and image, if the original object
has one.

Collection tiles may have a header and a footer; they also include additional
fields that help us configure the way it behaves: you can define how many
items the tile will shown as a maximun and an offset to start with items
different than the first one. This way you can create very simple and yet
powerful layout configurations with a couple of tiles and very few effort.

You can only drop 'Collection' objects on a Collection tile. Right now, you
can not edit individual items metadata directly in the tile. The title and
image fields will include a link to the original object location.

Content Body
++++++++++++

A Content Body tile shows a block of text of an object.

You can only drop 'Document' and 'News Item' objects into a Content Body tile.
Content Body tiles are not editable.

Embed
+++++

An Embed tile is used to embed external content in you cover page. Embed tile
fields includes title, description and the embedding code itself.

Embed tiles are only editable: you can not drop any object on it.

File
++++

A File tile shows metadata about a file and a link to download it. File tile
fields include title, description and the download link itself.

You can only drop 'File' objects into a File tiles. Fields in the tile will be
populated with the file metadata. All fields are user-editable, except for the
download link.

List
++++

A List tile shows a list of individual items; every item will show its title,
description and image, if the original object has one.

You can drop any object in a List tile. Items in the tile will be populated
with the objects metadata; if an object has an image, it will be shown also.
Right now, you can not edit individual items metadata in the list, but you can
remove or reorder them. The title and image fields will include a link to the
original object location.

Rich Text
+++++++++

A Rich Text tile shows a block of text; text can be edited using TinyMCE,
Plone standard web-based WYSIWYG editor. A Rich Text tile includes only one
text field.

You can only drop 'Document' objects into a Rich Text tile. The text field
will be populated with the object text. You can easily edit the text and you
can add images and links to it. Rich Text tiles support link-integrity: a
message will be shown if somebody tries to delete the object you are
referencing on the tile, warning her there is a link pointing to that object.

Using collective.cover
----------------------

Adding Cover
^^^^^^^^^^^^

.. figure:: https://raw.github.com/collective/collective.cover/master/docs/cover1.png
    :align: center
    :height: 312px
    :width: 367px

You add a cover like you would any type of content in Plone:

#. Navigate to the folder where you want to create a cover;

#. Open the "Add Item..." menu and choose "Cover";

#. Fill in the required fields:

    "Title" and "Description"
        Same as with other Plone content, like Page.
    "Layout"
        Choose one of the predefined cover layouts (you will see a preview of
        the selected layout).

#. "Save".

.. figure:: https://raw.github.com/collective/collective.cover/master/docs/cover1a.png
    :align: center
    :height: 600px
    :width: 680px

Your cover is now created based on the information provided.

Adding content in your Cover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the cover is created, you'll notice it comes with some predefined blocks
(according to the selected layout), but it still has no content associated.
To define the content that will appear on the cover, perform the following
steps:

.. figure:: https://raw.github.com/collective/collective.cover/master/docs/cover2.png
    :align: center
    :height: 460px
    :width: 680px

#. Select the "Compose" tab.

#. Open the "Add Content" tab to the right of the green bar. A small window
   will appear showing the most recent items added in the portal.

#. Select the title of any item in the list and drag it to one of the tiles
   (dotted boxes) in the content area.

#. Hover the item over one of the Tile boxes. Each Tile allows only certain
   types of content to be added. If the content you selected is allowed on
   that Tile, the box will turn green. If not, it will remain gray.

#. Release the item. Information from that content will be automatically
   applied to the chosen tile and will be visible on the cover.

#. Repeat the process to add content to each one of the other tiles.

#. To visualize the final result, select the "View" tab.

.. figure:: https://raw.github.com/collective/collective.cover/master/docs/cover3.png
    :align: center
    :height: 500px
    :width: 670px

There are also two other navigation options to find content.

Searching for content
+++++++++++++++++++++

You can use the search field in the content selection window to locate the
content you want:

#. Type the term you want to find.

#. Push the "Search" button.

The items related to the term you search will be displayed and can be used
according to the steps above.

Content tree
++++++++++++

Inside the content selection window you can also navigate through your site to
locate existing content.

#. Select the "Content Tree" tab.

#. Select the links to browse through the structure of your site until you
   find the desired content. All items listed are available to be used
   according to the steps above.

Editing a tile
^^^^^^^^^^^^^^

.. figure:: https://raw.github.com/collective/collective.cover/master/docs/cover6.png
    :align: center
    :height: 640px
    :width: 760px

After content is added to a cover tile, a copy of some of its information
will be stored in the cover and will appear to the end user. If necessary, you
can change some of the information related to the content exclusively for the
cover, without changing the information in the original item. This feature is
very useful to adjust the content for the cover. For example, you can shorten
a title to better fit it into a homepage layout.

To change the information on the cover, follow these steps:

#. Select the "Compose" tab.

#. Click the "Edit" link on the tile you want to change.

#. Select the portion of text you want to change, like the title, the
   description or any other text element.

#. Change the text and "Save".

The changes will be applied to your cover immediately.

.. Important::
    As mentioned before, the changes will be applied only to the cover tile,
    not to the original content.

Background image behavior
^^^^^^^^^^^^^^^^^^^^^^^^^

The package includes a behavior that adds the possibility of having a background image on the default view of the item.

To enable the behavior go to 'Site Setup' and select 'Dexterity content types'.
Look for 'Cover' content type, select it and then select 'Behaviors'.
Look for the 'Background image' behavior and enable it.
Now, when you add or edit a Cover item you will see a new field called 'Background image'.

.. figure:: https://raw.github.com/collective/collective.cover/master/docs/background-image-behavior-field.png
    :align: center
    :height: 480px
    :width: 728px

.. Tip::
    The background image will be shown using an inline style rule that is applied to the ``content`` ID selector.

Remember that, for accessibility reasons, you should not use background images as the sole method of conveying important information.

Advanced Actions
----------------

Changing the layout of your cover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have created a blank cover or if want to change the structure of your
current cover, you can add or delete tiles, change the position of an existing
tile, or even change the rows and columns structure of the cover. These
operations can be performed from the "Layout" tab.

.. figure:: https://raw.github.com/collective/collective.cover/master/docs/cover4.png
    :align: center
    :height: 427px
    :width: 696px

A cover is a combination of three basic elements:

- Rows (which may contain one or more columns, arranged horizontally)
- Columns (which may contain one or more tiles arranged vertically)
- Tiles

Adding rows and columns
+++++++++++++++++++++++

To add a new row, follow these steps:

#. In the Layout tab, click the Row icon and drag it to your page. Then you
   need to add one or more columns to this row so you can add tiles later.

#. Click on the Column icon and drag it into a row.

You can repeat this operation as often as you need. ``collective.cover`` will
divide the space between the rows and columns automatically.

Changing the width of columns
+++++++++++++++++++++++++++++

You can control the width of each column individually:

#. Push the configuration icon of the desired column.

#. Drag the slider sideways, adjusting the desired number of column widths.
   The higher the number, the larger the column width.

#. "Save".

.. figure:: https://raw.github.com/collective/collective.cover/master/docs/cover5.png
    :align: center
    :height: 450px
    :width: 670px

By default, ``collective.cover`` uses a grid of 16 units. Therefore, the sum
of the all widths in a column must not exceed 16. To make it easier to edit
the width of all columns, first adjust the width of the smallest column.

Adding new tiles
^^^^^^^^^^^^^^^^

Now that you have created columns, you can add tiles to it:

#. In the Layout tab, select one of the available Tile icons and drag it 
   to the column where you want to place it.

#. Change the configuration as desired.

#. Push "Save".

The new tile can be used in the Compose tab to select/add content.

Adjusting tiles
^^^^^^^^^^^^^^^

You can change the settings of previously added tiles at any time:

#. In the Layout tab, select the Setup icon of the respective tile.

#. Modify the information.

#. "Save".

Moving tiles around
^^^^^^^^^^^^^^^^^^^

On a page that has more than one column, you can conveniently move your tiles
around:

#. Select the "Layout" tab.

#. Click on a tile and drag it over another column in any of the rows.

#. When you release, the tile it will be positioned in the new column.

#. Repeat as often as necessary.

#. When finished, push "Save" and the new configuration will be applied.

Saving a layout as a model
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can save one of your covers as a template for creating other covers on
your website:

#. Select the Layout tab.

#. Click the "Export layout" button. 

#. Enter a name for your model.

#. Click "Export layout"".

Now this layout can be used as a model to create new covers, as explained in
the section "Adding a cover".
