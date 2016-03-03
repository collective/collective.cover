*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${tile_selector}  div.tile-container div.tile
${default_tile}  div.tile-default
${border_tile}  div.tile-edge
${border_class}  tile-edge
${tile_class}  div.cover-tile

*** Test cases ***

Test CSS Class
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description
    Open Layout Tab

    Add Tile  ${basic_tile_location}
    Save Cover Layout

    # now we move to the default view to check the default tile style
    Click Link  link=View
    Log Source
    Page Should Contain Element  css=${default_tile}

    # and now change style configuration
    # start with default style
    Open Layout Tab
    Click Config from Tile  ${tile_class}
    Wait until element is visible  id=buttons-save
    Click Button  id=buttons-save
    Save Cover Layout

    # go to View page and css remains
    Click Link  link=View
    Page Should Contain Element  css=${default_tile}

    # change style
    Open Layout Tab
    Click Config from Tile  ${tile_class}
    Select From List  css=select#collective-cover-basic-css_class  ${border_class}
    Wait until element is visible  id=buttons-save
    Click Button  id=buttons-save
    Save Cover Layout

    # go to View page and check new style
    Click Link  link=View
    Page Should Contain Element  css=${border_tile}


*** Keywords ***
Click Config from Tile
    [arguments]  ${tile}

    Click Element  css=${tile} .config-tile-link

