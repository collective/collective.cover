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

    Create Cover  Title  Description  Empty layout
    Click Link  link=Layout

    Add Tile  ${basic_tile_location}
    Save Cover Layout

    Click Link  link=Compose
    Page Should Contain   Please drag&drop some content here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${document_selector}  css=${tile_selector}
    Page Should Contain  My document

    Drag And Drop  css=${file_selector}  css=${tile_selector}
    Page Should Contain  My file
    Page Should Contain  This file was created for testing purposes

    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Page Should Contain  Test image
    Page Should Contain  This image was created for testing purposes

    Drag And Drop  css=${link_selector}  css=${tile_selector}
    Page Should Contain  Test link
    Page Should Contain  This link was created for testing purposes

    Drag And Drop  css=${news_item_selector}  css=${tile_selector}
    Page Should Contain  ${news_item_title}
    Page Should Contain  ${news_item_description}

    # now we move to the default view to check the information is still there
    Click Link  link=View
    Page Should Contain  ${news_item_title}
    Page Should Contain  ${news_item_description}

    # go back to compose view to edit title
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
