*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${file_tile_location}  "collective.cover.file"
${file_selector}  .ui-draggable .contenttype-file
${tile_selector}  div.tile-container div.tile
${title_field_id}  collective-cover-file-title
${title_sample}  Some text for title
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test File Tile
    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add tile to the layout
    Open Layout Tab
    Add Tile  ${file_tile_location}
    Save Cover Layout

    Compose Cover
    Page Should Contain  Please drag&drop a file here

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${file_selector}  css=${tile_selector}
    Wait Until Page Contains  My file
    Page Should Contain  This file was created for testing purposes
    Page Should Contain Link  link=Download file

    # go back to compose view and edit the tile
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit File Tile
    Input Text  id=${title_field_id}  ${title_sample}
    Click Button  Save
    Wait Until Page Does Not Contain  Edit File Tile

    # check for successful AJAX refresh
    Wait Until Page Contains  ${title_sample}

    Open Layout Tab
    Delete Tile
    Save Cover Layout
