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
    Create Cover  Title  Description  Empty layout

    Click Link  link=Layout
    Add Tile  ${banner_tile_location}
    Save Cover Layout

    Click Link  link=Compose
    Page Should Contain  Drag&drop an image or link here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button
    Drag And Drop  css=${news_item_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.banner-tile a img

    # now we move to the default view to check the information is still there
    Click Link  link=View
    Page Should Contain Image  css=div.banner-tile a img

    Click Link  link=Compose
    Page Should Not Contain  Drag&drop an image or link here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.banner-tile a img

    # now we move to the default view to check the element is still there
    Click Link  link=View
    Page Should Contain Image  css=div.banner-tile a img

    Click Link  link=Compose
    Page Should Not Contain  Drag&drop an image or link here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${link_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.banner-tile h2 a

    # now we move to the default view to check the link is still there
    Click Link  link=View
    Page Should Contain  Test link

    # now we test with a File content type to be sure that its getImage method doesn't
    # break the tile

    Click Link  link=Compose

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${file_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.banner-tile h2 a

    # go back to compose view to edit banner title
    Click Link  link=Compose
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_sample}
    # before saving, clean the banner tile to make sure it has been loaded
    # with the new text
    Execute Javascript  $('.tile').empty()
    Click Button  Save
    # save via ajax => wait until the tile has been reloaded
    Wait Until Page Contains  ${title_sample}

    # edit tile but don't save it
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_other_sample}
    Click Button  Cancel
    Page Should Not Contain Link  ${title_other_sample}
    Page Should Contain Link  ${title_sample}

    Click Link  link=Layout
    Delete Tile
    Save Cover Layout
