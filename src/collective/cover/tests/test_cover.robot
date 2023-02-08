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

*** Keywords ***

# BBB: Customization needed to avoid unlock error when we have delete content
# right after update. Wait a few seconds before update the content.
# Necessary only in Python 2.

Update
    [arguments]  ${title}  ${description}

    Click Link  link=Edit
    Sleep  5s  wait for unlock to work
    Input Text  css=${title_selector}  ${title}
    Input Text  css=${description_selector}  ${description}
    Click Button  Save
    Page Should Contain  Changes saved
