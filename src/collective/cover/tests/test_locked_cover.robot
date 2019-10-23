*** Settings ***

Documentation  Testing locked and unlocked
Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${ALT_ZOPE_HOST}  127.0.0.1
${ALT_PLONE_URL}  http://${ALT_ZOPE_HOST}:${ZOPE_PORT}/${PLONE_SITE_ID}
${LOCKED_MESSAGE}  This item was locked by
${basic_tile_location}  'collective.cover.basic'
${document_selector}  .ui-draggable .contenttype-document
${tile_selector}  div.tile-container div.tile


*** Keywords ***

# FIXME: Override the plone.app.robotframework 'Log in' keyword.
# The original keyword doesn't work in Plone 4.3. 
# See: https://github.com/plone/plone.app.robotframework/issues/107
Log in
    [Documentation]  Log in to the site as ${userid} using ${password}. There
    ...              is no guarantee of where in the site you are once this is
    ...              done. (You are responsible for knowing where you are and
    ...              where you want to be)
    [Arguments]  ${userid}  ${password}
    Go to  ${PLONE_URL}/login_form
    Page should contain element  __ac_name
    Page should contain element  __ac_password
    Page should contain element  css=#login-form .formControls input[name=submit]
    Input text for sure  __ac_name  ${userid}
    Input text for sure  __ac_password  ${password}
    Click Button  css=#login-form .formControls input[name=submit]

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
    Wait Until Page Contains  ${LOCKED_MESSAGE}

    Switch Browser  1
    Click Link  link=View
    Page Should Not Contain  ${LOCKED_MESSAGE}

    Switch Browser  2
    Click Link  link=My Cover
    Page Should Not Contain  ${LOCKED_MESSAGE}
    Compose Cover

    Switch Browser  1
    Click Link  link=My Cover
    Wait Until Page Contains  ${LOCKED_MESSAGE}

    Switch Browser  2
    Click Link  link=View
    Page Should Not Contain  ${LOCKED_MESSAGE}

    Switch Browser  1
    Click Link  link=My Cover
    Page Should Not Contain  ${LOCKED_MESSAGE}
    Open Layout Tab

    Switch Browser  2
    Click Link  link=My Cover
    Wait Until Page Contains  ${LOCKED_MESSAGE}

    Switch Browser  1
    Click Link  link=View
    Page Should Not Contain  ${LOCKED_MESSAGE}

    Switch Browser  2
    Click Link  link=My Cover
    Page Should Not Contain  ${LOCKED_MESSAGE}
    Open Layout Tab

    Switch Browser  1
    Click Link  link=My Cover
    Wait Until Page Contains  ${LOCKED_MESSAGE}
