*** Settings ***

Documentation  Testing locked and unlocked
Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${ALT_ZOPE_HOST}  127.0.0.1
${ALT_PLONE_URL}  http://${ALT_ZOPE_HOST}:${ZOPE_PORT}/${PLONE_SITE_ID}
${LOCKED_MESSAGE}  This item was locked by admin 1 minute ago.
${basic_tile_location}  'collective.cover.basic'
${document_selector}  .ui-draggable .contenttype-document
${tile_selector}  div.tile-container div.tile

*** Test Cases ***

Test Locked Cover
    Log in as site owner
    Goto Homepage
    Create Cover  My Cover  Description
    Open Layout Tab

    Add Tile  ${basic_tile_location}
    Save Cover Layout

    Compose Cover
    Page Should Contain   Please drag&drop some content here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${document_selector}  css=${tile_selector}
    Page Should Contain  My document

    Click Link  link=My Cover
    Compose Cover

    # open a new browser to simulate a 2-user interaction
    Open Browser  ${ALT_PLONE_URL}
    Enable Autologin as  Site Administrator
    Goto Homepage
    Click Link  link=My Cover
    Page Should Contain  Locked  ${LOCKED_MESSAGE}

    Switch Browser  1
    Click Link  link=View
    Page Should Not Contain  Locked  ${LOCKED_MESSAGE}

    Switch Browser  2
    Click Link  link=My Cover
    Page Should Not Contain  Locked  ${LOCKED_MESSAGE}
    Compose Cover

    Switch Browser  1
    Click Link  link=My Cover
    Page Should Contain  Locked  ${LOCKED_MESSAGE}

    Switch Browser  2
    Click Link  link=View
    Page Should Not Contain  Locked  ${LOCKED_MESSAGE}

    Switch Browser  1
    Click Link  link=My Cover
    Page Should Not Contain  Locked  ${LOCKED_MESSAGE}
    Open Layout Tab

    Switch Browser  2
    Click Link  link=My Cover
    Page Should Contain  Locked  ${LOCKED_MESSAGE}

    Switch Browser  1
    Click Link  link=View
    Page Should Not Contain  Locked  ${LOCKED_MESSAGE}

    Switch Browser  2
    Click Link  link=My Cover
    Page Should Not Contain  Locked  ${LOCKED_MESSAGE}
    Open Layout Tab

    Switch Browser  1
    Click Link  link=My Cover
    Page Should Contain  Locked  ${LOCKED_MESSAGE}
