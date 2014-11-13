*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${banner_tile_location}  'collective.cover.banner'
${image_selector}  .ui-draggable .contenttype-image
${link_selector}  .ui-draggable .contenttype-link
${news_item_selector}  .ui-draggable .contenttype-news-item
${file_selector}  .ui-draggable .contenttype-file
${tile_selector}  div.tile-container div.tile
${title_field_id}  collective-cover-banner-title
${title_sample}  Some text for title
${title_other_sample}  This text should never be saved
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test Banner Tile
    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add a banner tile to the layout
    Edit Cover Layout
    Page Should Contain  Export layout
    Add Tile  ${banner_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain  Drag&drop an image or link here to populate the tile.

    # drag&drop an Image
    Open Content Chooser
    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.cover-banner-tile a img

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain Image  css=div.cover-banner-tile a img

    # drag&drop a News Item; its image should populate the tile
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${news_item_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.cover-banner-tile a img

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain Image  css=div.cover-banner-tile a img

    # drag&drop a Link
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${link_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.cover-banner-tile h2 a

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  Test link

    # drag&drop a File; its getImage method should not break the tile
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${file_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.cover-banner-tile h2 a

    # edit the tile and check AJAX refresh
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_sample}
    Click Button  Save
    Wait Until Page Contains  ${title_sample}

    # edit the tile but cancel operation
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_other_sample}
    Click Button  Cancel
    Wait Until Page Contains  ${title_sample}

    # delete the tile
    Edit Cover Layout
    Delete Tile
    Save Cover Layout
