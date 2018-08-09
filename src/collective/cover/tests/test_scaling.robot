*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_name} =  "collective.cover.basic"
${image_selector}  //fieldset[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Image"]/span[text()='Test image']/..
${tile_selector}  div.tile-container div.tile
${tile_class} =  div.cover-tile

*** Test cases ***

Test Scaling
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description

    Open Layout Tab

    Add Tile  ${basic_tile_name}
    Save Cover Layout

    Compose Cover
    Open Content Chooser
    Click Element  link=Content tree
    Drag And Drop  xpath=${image_selector}  css=${tile_selector}

    Click Link  link=View
    Page Should Contain Element  xpath=//img[@width=50][@height=50]

    Open Layout Tab
    Click Config from Tile  ${tile_class}
    Wait until element is visible  id=buttons-cancel
    Select From List  css=#collective-cover-basic-image-imgsize  listing 16x16
    Click Button  id=buttons-save
    Save Cover Layout

    Click Link  link=View
    Page Should Contain Element  xpath=//img[@width=16][@height=16]

    Open Layout Tab
    Click Config from Tile  ${tile_class}
    Wait until element is visible  id=buttons-cancel
    Select From List  css=#collective-cover-basic-image-imgsize  icon 32x32
    Click Button  id=buttons-save
    Save Cover Layout

    Click Link  link=View
    Page Should Contain Element  xpath=//img[@width=32][@height=32]


*** Keywords ***

Click Config from Tile
    [arguments]  ${tile}

    Click Element  css=${tile} .config-tile-link
