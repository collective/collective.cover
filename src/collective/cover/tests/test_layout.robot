*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_name} =  "collective.cover.basic"
${tile_class} =  div.cover-tile

*** Test cases ***

Test Basic Layout Operations
    [Tags]  Mandelbug

    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description
    Open Layout Tab
    # empty layout has one column and one row by default
    # TODO: test if there is 1 row and 1 column
    #       this can be done using Xpath Should Match X Times
    #       http://rtomac.github.com/robotframework-selenium2library/doc/Selenium2Library.html#Xpath%20Should%20Match%20X%20Times

    #count if there is 1 row and 1 column

    Count Number of Columns  1
    Count Number of Rows  1

    #add a row after the existing one.
    #it comes with a new column
    Add Row

    # trying to leave layout editing without saving must show a warning
    Choose Cancel On Next Confirmation
    Click Link  link=Compose
    Confirm Action
    # continue editing layout

    #add a column in the latest row
    Add Column at First Row
    Add Column at Second Row
    Add Column at Second Row

    #5 columns and 2 rows
    Count Number of Columns  5
    Count Number of Rows  2

    Save Cover Layout

    # load layout again, it has to be the new one
    Open Layout Tab

    #3 columns and 2 rows
    Count Number of Columns  5
    Count Number of Rows  2

    Delete a Column in the First Row
    Delete the First Row

    Count Number of Columns  3
    Count Number of Rows  1

    Save Cover Layout

    Add Tile  ${basic_tile_name}
    Delete Tile

    #add tile, and check if clicking in the config icon opens an overlay
    Add Tile  ${basic_tile_name}
    Click Config from Tile  ${tile_class}
    Wait until element is visible  id=buttons-cancel
    # Move Categories to second place
    Drag And Drop  css=#formfield-collective-cover-basic-subjects label  css=#configure_tile div.field:nth-child(2) label
    # Move Date over Categories
    Drag And Drop  css=#formfield-collective-cover-basic-date label  css=#formfield-collective-cover-basic-subjects label
    # Try to move Date over CSS
    Drag And Drop  css=#formfield-collective-cover-basic-date label  css=#formfield-collective-cover-basic-css_class label
    # Hide Description
    Click Element  css=#formfield-collective-cover-basic-description .visibility-no
    Click Button  id=buttons-save
    # Change row class
    Click Element  css=.config-row-link:nth-child(1)
    Wait until element is visible  id=class-chooser
    Click Button  css=#class-chooser .cssclasswidget
    Click Element  css=.cssclasswidget-tile-shadow
    Click Element  css=.cssclasswidget-overlay
    Click Element  css=.ui-dialog:last-child .ui-dialog-titlebar-close
    # Change column class
    Click Element  css=.config-column-link:nth-child(1)
    Wait until element is visible  id=class-chooser
    Click Button  css=#class-chooser .cssclasswidget
    Click Element  css=.cssclasswidget-tile-edge
    Click Element  css=.cssclasswidget-overlay
    Click Element  css=.ui-dialog:last-child .ui-dialog-titlebar-close
    Save Cover Layout

    # Test row and column classes
    Compose Cover
    Page Should Contain Element  css=.row.tile-shadow
    Page Should Contain Element  css=.cell.tile-edge
    Click Link  link=View
    Page Should Contain Element  css=.row.tile-shadow
    Page Should Contain Element  css=.cell.tile-edge


    # Reopen Layout and check configuration
    Open Layout Tab
    Click Config from Tile  ${tile_class}
    Wait until element is visible  id=buttons-cancel
    # Date should be first in order (order is 1-indexed)
    Textfield Value Should Be  css=#collective-cover-basic-date-order  1
    # Categories should be second in order
    Textfield Value Should Be  css=#collective-cover-basic-subjects-order  2
    # Description should be hidden
    Checkbox Should Not Be Selected  css=#collective-cover-basic-description-visibility-yes
    Checkbox Should Be Selected  css=#collective-cover-basic-description-visibility-no
    Click Button  id=buttons-cancel



*** Keywords ***

Add Row
    #we can't control the drop position, but is always at the last position
    Drag And Drop  css=${row_button_selector}  css=${row_drop_area_selector}

Add Column at First Row
    Drag And Drop  css=${column_button_selector}  css=div.layout div.cover-row:nth-of-type(1)

Add Column at Second Row
    Drag And Drop  css=${column_button_selector}  css=div.layout div.cover-row:nth-of-type(2)

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
