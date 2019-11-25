*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_name} =  "collective.cover.basic"
${xpath-size} = //*[@id="content"]/div[2]/div/div@data-column-size
${xpath-text} = //*[@id="column-size-resize"]/span

*** Test cases ***

Test Columns-Titles and Resize

    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Save-Cover  Test-cover
    Open Layout Tab
    Add Tile  ${basic_tile_name}
    ${data-size-before}=  Get Element Attribute  xpath=${xpath-size}
    Click Element  css=i.resizer
    Wait until element is visible  id=ui-id-1
    ${data-text-before}=  Get Text  xpath=${xpath-text}
    Drag And Drop By Offset  css=a.ui-slider-handle.ui-state-default.ui-corner-all  -30  0
    ${data-text-after}=  Get Text  xpath=${xpath-text}
    Should Be True  """${data-text-before}""" != """${data-text-after}"""
    Click Element  css=.ui-dialog-titlebar-close
    Save Cover Layout
    Click Link  link=Compose
    Open Layout Tab
    ${data-size-after}=  Get Element Attribute  xpath=${xpath-size}
    Should Be True  """${data-size-before}""" != """${data-size-after}""" 
