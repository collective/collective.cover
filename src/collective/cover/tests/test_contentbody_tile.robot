*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote


Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${contentbody_tile_location}  'collective.cover.contentbody'
${document_selector}  .ui-draggable .contenttype-document
${tile_selector}  div.tile-container div.tile
${text_sample}  Some text for document
${edit_link_selector}  a.edit-tile-link
${document_body}  body.portaltype-document

*** Test cases ***

Test Content Body Tile
    Enable Autologin as  Site Administrator

    # edit document so it contains text
    Click Link  link=My document
    Click Link  link=Edit
    Input Text  id=text  ${text_sample}
    Click Button  Save
    Page Should Contain  ${text_sample}

    # create cover
    Go to Homepage
    Create Cover  My Cover  Description

    # add a content body tile to the layout
    Edit Cover Layout
    Page Should Contain  Export layout
    Add Tile  ${contentbody_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain  Drag&drop some content to populate the tile.

    # drag&drop a Document
    Open Content Chooser
    Drag And Drop  css=${document_selector}  css=${tile_selector}
    Wait Until Page Contains  ${text_sample}
    Page Should Not Contain  Drag&drop some content to populate the tile.

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  ${text_sample}
    Page Should Not Contain  Drag&drop some content to populate the tile.

    # when content chooser is opened again , the tile has a link to the referenced item
    Compose Cover
    Page Should Contain  Go to related item
    Click Link  link=Go to related item
    Page Should Contain  My document
    Page Should Contain Element  css=${document_body}

    # this tile has no configuration option
    Click Link  link=My Cover
    Compose Cover
    Page Should Not Contain  css=${edit_link_selector}

    # delete the tile
    Edit Cover Layout
    Delete Tile
    Save Cover Layout
