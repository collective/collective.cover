*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_name} =  "collective.cover.basic"
${tile_class} =  div.cover-tile

*** Test cases ***

Test Columns-Titles and Resize

    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Save-Cover  Test-cover
    Open Layout Tab

    Add Tile  ${basic_tile_name}
    Click Element  css=i.resizer
    Wait until element is visible  id=ui-id-1
    Drag And Drop By Offset  css=a.ui-slider-handle.ui-state-default.ui-corner-all  -30  0
    Click Element  css=.ui-dialog-titlebar-close

    Save Cover Layout

    Click Link  link=Compose
    Open Layout Tab

    ${data-column-size}=  Get Element Attribute  xpath=/html/body/div[1]/div[2]/div/div[2]/div[2]/div[2]/div/div@data-column-size  

    Should Be Equal  ${data-column-size}  14 
    
    Delete the First Row

*** Keywords ***

Delete the First Row
    Click Element  css=div.cover-row:nth-of-type(1) > button.close
Cancel Add Tile
    Element Should Be Visible  css=${tile_cancel_area_selector}
    Click Element  css=${tile_cancel_area_selector}
    Element Should Not Be Visible  css=${tile_cancel_area_selector}
