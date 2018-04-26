*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote
Library  ${CURDIR}/LinkIntegrityUtils.py

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers
Test Setup  Setup Link Integrity
Test Teardown  Teardown Link Integrity

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${richtext_tile_location}  'collective.cover.richtext'
${document_selector}  .ui-draggable .contenttype-document
${tile_selector}  div.tile-container div.tile
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test Link Integrity on Basic Tile
    [Tags]  issue_615
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
    Click Button  Cancel

Test Link Integrity on RichText Tile
    [Tags]  issue_615
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
    Click Button  Cancel

*** Keywords ***

Edit RichText Tile
    [arguments]  ${html}

    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Rich Text Tile
    Sleep  1s  Wait for TinyMCE to load
    Wait For Condition  return typeof tinyMCE !== "undefined" && tinyMCE.activeEditor !== null && document.getElementById(tinyMCE.activeEditor.id) !== null
    Execute Javascript  tinyMCE.activeEditor.setContent('${html}');
    Click Button  Save
    Wait Until Page Does Not Contain  Edit Rich Text Tile
