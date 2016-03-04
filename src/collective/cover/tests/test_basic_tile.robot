*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote
Library  ${CURDIR}/TestInternalServerError.py

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

# XXX: test is randomly failing under Plone 4.2 only
Default Tags  Mandelbug

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${document_selector}  .ui-draggable .contenttype-document
${file_selector}  .ui-draggable .contenttype-file
${image_selector}  .ui-draggable .contenttype-image
${link_selector}  .ui-draggable .contenttype-link
${tile_selector}  div.tile-container div.tile
${news_item_selector}  .ui-draggable .contenttype-news-item
${news_item_title}  Test news item
${news_item_description}  This news item was created for testing purposes
${title_field_id}  collective-cover-basic-title
${title_sample}  Some text for title
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test Basic Tile
    # XXX: test is randomly failing under Plone 4.2 only
    Run keyword if  '${CMFPLONE_VERSION}' >= '4.3'  Remove Tags  Mandelbug

    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add tile to the layout
    Open Layout Tab
    Add Tile  ${basic_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain   Please drag&drop some content here to populate the tile.

    # drag&drop a Document
    Open Content Chooser
    Drag And Drop  css=${document_selector}  css=${tile_selector}
    Page Should Contain  My document

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  My document

    # drag&drop a File
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${file_selector}  css=${tile_selector}
    Page Should Contain  My file

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  My file

    # drag&drop an Image
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.cover-basic-tile a img

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  Test image

    # drag&drop an Image, forcing an error in the server. This error is made
    # possible using the keyword below from TestInternalServerError.py Library.
    Apply Patch Populate With Object
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.cover-basic-tile a img
    Page Should Contain  Internal Server Error
    Remove Patch Populate With Object

    # drag&drop a Link
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${link_selector}  css=${tile_selector}
    Page Should Contain  Test link

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  Test link

    # drag&drop a News Item
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${news_item_selector}  css=${tile_selector}
    Page Should Contain  ${news_item_title}
    Page Should Contain  ${news_item_description}

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  ${news_item_title}
    Page Should Contain  ${news_item_description}

    # go back to compose view and edit the tile
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Basic Tile
    Input Text  id=${title_field_id}  ${title_sample}
    Click Button  Save
    Wait Until Page Does Not Contain  Edit Basic Tile

    # check for successful AJAX refresh
    Wait Until Page Contains  ${title_sample}

    Open Layout Tab
    Delete Tile
    Save Cover Layout
