*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

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
${title_other_sample}  This text should never be saved
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test Basic Tile
    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add a Basic tile to the layout
    Edit Cover Layout
    Page Should Contain  Export layout
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
    Page Should Contain  Test image

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  Test image

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

    # go back to compose view to edit title
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_sample}
    Click Button  Save
    # save via ajax => wait until the tile has been reloaded
    Wait Until Page Contains  ${title_sample}

    # edit tile but don't save it
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_other_sample}
    Click Button  Cancel
    Page Should Not Contain Link  ${title_other_sample}
    Page Should Contain Link  ${title_sample}

    Edit Cover Layout
    Delete Tile
    Save Cover Layout
