*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${list_tile_location}  'collective.cover.list'
${document_selector}  .ui-draggable .contenttype-document
${file_selector}  .ui-draggable .contenttype-file
${image_selector}  .ui-draggable .contenttype-image
${link_selector}  .ui-draggable .contenttype-link
${news-item_selector}  .ui-draggable .contenttype-news-item
${tile_selector}  div.tile-container div.tile

${first_item}  .list-item:first-child
${last_item}   .list-item:last-child

*** Test cases ***

Test List Tile
    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description  Empty layout

    # add a list tile to the layout
    Edit Cover Layout
    Add Tile  ${list_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain  Please add up to 5 objects to the tile.

    # only on the compose view though, the default view stays empty
    Click Link  link=View
    Page Should Not Contain  Please add up to 5 objects to the tile.

    # drag&drop a Document
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${document_selector}  css=${tile_selector}
    Wait Until Page Contains  My document
    Page Should Contain  This document was created for testing purposes

    # drag&drop a File
    Drag And Drop  css=${file_selector}  css=${tile_selector}
    Wait Until Page Contains  My file
    Page Should Contain  This file was created for testing purposes

    # drag&drop an Image
    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Wait Until Page Contains  Test image
    Page Should Contain  This image was created for testing purposes

    # drag&drop a Link
    Drag And Drop  css=${link_selector}  css=${tile_selector}
    Wait Until Page Contains  Test link
    Page Should Contain  This link was created for testing purposes

    # drag&drop a News Item
    Drag And Drop  css=${news-item_selector}  css=${tile_selector}
    Wait Until Page Contains  Test news item
    Page Should Contain  This news item was created for testing purposes

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Not Contain  Please add up to 5 objects to the tile.
    Page Should Contain  My document
    Page Should Contain  My file
    Page Should Contain  Test image
    Page Should Contain  Test link
    Page Should Contain  Test news item

    # reorder list items
    Compose Cover

    # check the existing order
    ${first_item_title} =  Get Text  css=${first_item} h2
    ${last_item_title} =  Get Text  css=${last_item} h2
    Should Be Equal  ${first_item_title}  My document
    Should Be Equal  ${last_item_title}  Test news item

    # move first item to the end

    # Selenium doesn't seem to handle drag&drop correctly if the
    # drop-target is not in the viewport. This code tries to work
    # around the issue.
    Execute Javascript    window.scroll(0, 800)

    Drag And Drop  css=${first_item}  css=${last_item}
    Sleep  1s  Wait for reordering to occur

    # ensure that the reodering is reflected in the DOM
    ${first_item_title} =  Get Text  css=${first_item} h2
    ${last_item_title} =  Get Text  css=${last_item} h2
    Should Be Equal  ${first_item_title}  My file
    Should Be Equal  ${last_item_title}  My document

    # delete the tile
    Edit Cover Layout
    Delete Tile
    Save Cover Layout
