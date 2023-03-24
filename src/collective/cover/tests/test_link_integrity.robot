*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote
Library  ${CURDIR}/LinkIntegrityUtils.py

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${richtext_tile_location}  'collective.cover.richtext'
${document_selector}  .ui-draggable .contenttype-document
${tile_selector}  div.tile-container div.tile

*** Test cases ***

Test Link Integrity on Basic Tile
    Enable Autologin as  Manager
    Go to Homepage
    Create Cover  Title  Description

    # add tile to the layout
    Open Layout Tab
    Add Tile  ${basic_tile_location}
    Save Cover Layout

    # drag&drop a Document
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${document_selector}  css=${tile_selector}
    Page Should Contain  My document

    # a warning is shown when trying to delete the document
    Go to Homepage
    Click Link  link=My document
    Click Delete Action
    Wait Until Page Contains  Potential link breakage
    Click Button  css=${cancel_delete_selector}

Test Link Integrity on RichText Tile
    Enable Autologin as  Manager
    Go to Homepage
    Create Cover  Title  Description

    # add tile to the layout
    Open Layout Tab
    Add Tile  ${richtext_tile_location}
    Save Cover Layout

    # add an internal link to a Document
    Compose Cover
    # use a helper function to get the UUID of the document
    ${html} =  Get Internal Link HTML Code
    Edit RichText Tile  ${html}

    # a warning is shown when trying to delete the document
    Go to Homepage
    Click Link  link=My document
    Click Delete Action
    Wait Until Page Contains  Potential link breakage
    Click Button  css=${cancel_delete_selector}

*** Keywords ***

Edit RichText Tile
    [arguments]  ${html}

    Click Edit Cover
    Wait Until Page Contains  Edit Rich Text Tile
    Input RichText  ${html}
    Click Button  css=${save_edit_selector}
    Wait Until Page Does Not Contain  Edit Rich Text Tile
