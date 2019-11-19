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
    Drag And Drop By Offset  css=a.ui-slider-handle.ui-state-default.ui-corner-all  -30  0
    Drag And Drop By Offset  css=a.ui-slider-handle.ui-state-default.ui-corner-all  -30  0
    Click Element  css=.ui-dialog-titlebar-close
    #count if there is 1 row and 1 column
    Count Number of Columns  1
    Count Number of Rows  1
    
    #Add elements
    Add Tile  ${basic_tile_name} 
    Add Row
    Add Column at First Row
    Add Column at First Row
    Add Column at Second Row
    Add Tile  ${basic_tile_name}

    #Check number of columns
    Count Number of Columns  5

    Save Cover Layout

    Click Link  link=Compose
    Open Layout Tab

    Add Column at Second Row
    Add Column at Second Row
    Add Column at Second Row
    Add Column at First Row
    Add Row
    Add Column at Third Row
    Add Tile  ${basic_tile_name}



    #check new elemets
    Count Number of Columns  10
    Count Number of Rows  3
    Delete the First Row

*** Keywords ***

Add Row
    #we can't control the drop position, but is always at the last position
    Drag And Drop  css=${row_button_selector}  css=${row_drop_area_selector}

Add Column at First Row
    Drag And Drop  css=${column_button_selector}  css=div.layout div.cover-row:nth-of-type(1)

Add Column at Second Row
    Drag And Drop  css=${column_button_selector}  css=div.layout div.cover-row:nth-of-type(2)

Add Column at Third Row
    Drag And Drop  css=${column_button_selector}  css=div.layout div.cover-row:nth-of-type(3)

Delete the First Row
    Click Element  css=div.cover-row:nth-of-type(1) > button.close

Delete a Column in the First Row
    Click Element  css=div.layout div.cover-row:nth-of-type(1) div.cover-column:nth-of-type(1) > button.close

Cancel Add Tile
    Element Should Be Visible  css=${tile_cancel_area_selector}
    Click Element  css=${tile_cancel_area_selector}
    Element Should Not Be Visible  css=${tile_cancel_area_selector}

Select Tile to Add
    [arguments]  ${tile}

    Click Element  xpath=//div[contains(@class, "tile-select-button") and contains(text(), ${tile})]

Delete Tile
    Click Element  css=div.cover-tile button.close

Count Number of Columns
    [arguments]  ${number}

    Xpath Should Match X Times  //div[contains(@class, 'cover-row')]//div[contains(@class, 'cover-column')]  ${number}


Count Number of Rows
    [arguments]  ${number}

    Xpath Should Match X Times  //div[contains(@class, 'cover-row')]  ${number}

Click Config from Tile
    [arguments]  ${tile}

    Click Element  css=${tile} .config-tile-link
