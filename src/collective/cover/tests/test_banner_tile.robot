*** Settings ***

Library  Selenium2Library  timeout=10 seconds  implicit_wait=5 seconds
Resource  keywords.txt
Resource  cover_keywords.txt
Variables  plone/app/testing/interfaces.py

Suite Setup  Start Browser and Log In
Suite Teardown  Close Browser

*** Variables ***

${banner_tile_location}  'collective.cover.banner'
${banner_uuid}  12345
${image_selector}  .ui-draggable .contenttype-image
${link_selector}  .ui-draggable .contenttype-link
${tile_selector}  div.tile-container div.tile

*** Test cases ***

Test Banner Tile
    Create Cover  Title  Description  Empty layout
    Click Link  link=Layout

    Add Tile  ${banner_tile_location}
    Save Cover Layout

    Click Link  link=Compose
    Page Should Contain  Drag&drop an image or link here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Page Should Contain Image  css=div.banner-tile a img

    # now we move to the default view to check the element is still there
    Click Link  link=View
    Page Should Contain Image  css=div.banner-tile a img

    Click Link  link=Compose
    Page Should Not Contain  Drag&drop an image or link here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${link_selector}  css=${tile_selector}
    Page Should Contain Link  css=div.banner-tile h2 a

    # now we move to the default view to check the link is still there
    Click Link  link=View
    Page Should Contain  Test link

    Click Link  link=Layout
    Delete Tile
    Save Cover Layout
