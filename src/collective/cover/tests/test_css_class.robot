*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${tile_selector}  div.tile-container div.tile
${default_class}  tile-default
${border_class}  tile-edge
${shadow_class}  tile-shadow
${dark_class}  tile-dark
${tile_class}  div.cover-tile

*** Test cases ***

Test CSS Classes
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description
    Open Layout Tab

    Add Tile  ${basic_tile_location}
    Save Cover Layout

    # now we move to the default view to check the default tile style
    Click Link  link=View
    Log Source
    Page Should Contain Element  css=div.${default_class}

    # and now change style configuration
    # start with default style
    Open Layout Tab
    Click Config from Tile  ${tile_class}
    Wait until element is visible  id=buttons-save
    Click Button  id=buttons-save
    Save Cover Layout

    # go to View page and css remains
    Click Link  link=View
    Page Should Contain Element  css=div.${default_class}

    # change style
    Open Layout Tab
    Click Config from Tile  ${tile_class}
    Click Button  css=#formfield-collective-cover-basic-css_class .cssclasswidget
    Click Element  css=.cssclasswidget-${border_class}
    Click Element  css=.cssclasswidget-overlay
    Wait until element is visible  id=buttons-save
    Click Button  id=buttons-save
    Save Cover Layout

    # go to View page and check new style
    Click Link  link=View
    Page Should Contain Element  css=div.${border_class}

    Open Layout Tab
    Click Config from Tile  ${tile_class}
    Click Button  css=#formfield-collective-cover-basic-css_class .cssclasswidget
    Click Element  css=.cssclasswidget-${shadow_class}
    Click Element  css=.cssclasswidget-overlay
    Wait until element is visible  id=buttons-save
    Click Button  id=buttons-save
    Save Cover Layout

    # go to View page and check new style
    Click Link  link=View
    Page Should Contain Element  css=div.${border_class}.${shadow_class}

    Open Layout Tab
    Click Config from Tile  ${tile_class}
    Click Button  css=#formfield-collective-cover-basic-css_class .cssclasswidget
    Click Element  css=.cssclasswidget-${dark_class}
    Click Element  css=.cssclasswidget-overlay
    Wait until element is visible  id=buttons-save
    Click Button  id=buttons-save
    Save Cover Layout

    # go to View page and check new style
    Click Link  link=View
    Page Should Contain Element  css=div.${border_class}.${shadow_class}.${dark_class}


*** Keywords ***
Click Config from Tile
    [arguments]  ${tile}

    Click Element  css=${tile} .config-tile-link

