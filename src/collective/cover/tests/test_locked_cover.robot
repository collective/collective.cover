*** Settings ***

Documentation  Testing locked and unlocked
Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${OWNER2_NAME}      admin2
${OWNER2_PASSWORD}  admin2
${basic_tile_location}  'collective.cover.basic'
${document_selector}  .ui-draggable .contenttype-document
${tile_selector}  div.tile-container div.tile

*** Test Cases ***

Test Locked Cover
    Log in as site owner
    Goto Homepage

    Create new user
    Goto Homepage

    Create Cover  My Cover  Description
    Edit Cover Layout

    Add Tile  ${basic_tile_location}
    Save Cover Layout

    Compose Cover
    Page Should Contain   Please drag&drop some content here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${document_selector}  css=${tile_selector}
    Page Should Contain  My document

    Click Link  link=My Cover
    Compose Cover

    Open Browser  http://127.0.0.1:${PORT}/plone
    Goto  ${PLONE_URL}/login_form
    Page should contain element  __ac_name
    Input text  __ac_name  ${OWNER2_NAME}
    Input text  __ac_password  ${OWNER2_PASSWORD}
    Click Button  Log in

    Switch Browser  2
    Click Link  link=My Cover
    Page Should Contain   Locked    This item was locked by admin 1 minute ago.

    Switch Browser  1
    Click Link  link=View
    Page Should Not Contain   Locked    This item was locked by admin 1 minute ago.

    Switch Browser  2
    Click Link  link=My Cover
    Page Should Not Contain   Locked    This item was locked by admin 1 minute ago.
    Compose Cover

    Switch Browser  1
    Click Link  link=My Cover
    Page Should Contain   Locked    This item was locked by admin 1 minute ago.

    Switch Browser  2
    Click Link  link=View
    Page Should Not Contain   Locked    This item was locked by admin 1 minute ago.

    Switch Browser  1
    Click Link  link=My Cover
    Page Should Not Contain   Locked    This item was locked by admin 1 minute ago.
    Edit Cover Layout

    Switch Browser  2
    Click Link  link=My Cover
    Page Should Contain   Locked    This item was locked by admin 1 minute ago.

    Switch Browser  1
    Click Link  link=View
    Page Should Not Contain   Locked    This item was locked by admin 1 minute ago.

    Switch Browser  2
    Click Link  link=My Cover
    Page Should Not Contain   Locked    This item was locked by admin 1 minute ago.
    Edit Cover Layout

    Switch Browser  1
    Click Link  link=My Cover
    Page Should Contain   Locked    This item was locked by admin 1 minute ago.
    Close Browser

    Switch Browser  2
    Close Browser

*** Keywords ***

Create new user
    # XXX: there's no need to do this here; it's better to prepare it programmatically
    Goto  ${PLONE_URL}/@@usergroup-userprefs
    Click Button  Add New User
    Input text  form.fullname  ${OWNER2_NAME}
    Input text  form.username  ${OWNER2_PASSWORD}
    Input text  form.email  ${OWNER2_NAME}@null.com
    Input Password  form.password  ${OWNER2_NAME}
    Input Password  form.password_ctl  ${OWNER2_PASSWORD}
    Select Checkbox  form.groups.0
    Click Button  Register
