*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open Test Browser
Test Teardown  Close all browsers

*** Test cases ***

Test CRUD
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description
    Update  Title fixed  Description fixed
    Delete

Test renderBase
    Enable Autologin as  Site Administrator
    Goto Homepage

    Create Cover  Title  Description
    ${BASE}  Get Element Attribute  tag=base@href
    Should Be Equal  ${BASE}  ${PLONE_URL}/title-1/
    Compose Cover
    ${BASE}  Get Element Attribute  tag=base@href
    Should Be Equal  ${BASE}  ${PLONE_URL}/title-1/
    Open Layout Tab
    ${BASE}  Get Element Attribute  tag=base@href
    Should Be Equal  ${BASE}  ${PLONE_URL}/title-1/

*** Keywords ***

Update
    [arguments]  ${title}  ${description}

    Click Link  link=Edit
    Input Text  css=${title_selector}  ${title}
    Input Text  css=${description_selector}  ${description}
    Click Button  Save
    Page Should Contain  Changes saved

Delete
    Open Action Menu
    Log Source
    Click Link  css=a#plone-contentmenu-actions-delete
    Click Button  Delete
    Page Should Contain  Plone site
