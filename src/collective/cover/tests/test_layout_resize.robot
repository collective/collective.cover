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
    ${data-column-size_before}=  Get Element Attribute  xpath=//*[@id="content"]/div[2]/div/div@data-column-size
    Click Element  css=i.resizer
    Wait until element is visible  id=ui-id-1
    Drag And Drop By Offset  css=a.ui-slider-handle.ui-state-default.ui-corner-all  -30  0
    Click Element  css=.ui-dialog-titlebar-close
    Save Cover Layout
    Click Link  link=Compose
    Open Layout Tab
    ${data-column-size_aftere}=  Get Element Attribute  xpath=//*[@id="content"]/div[2]/div/div@data-column-size  
    Should Be True  ${data-column-size_before} != ${data-column-size_after} 
