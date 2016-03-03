*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Variables  plone/app/testing/interfaces.py

*** Variables ***

${PORT} =  55001
${ZOPE_URL} =  http://localhost:${PORT}
${PLONE_URL} =  ${ZOPE_URL}/plone
${BROWSER} =  Firefox

${title_selector} =  input#form-widgets-IBasic-title
${description_selector} =  textarea#form-widgets-IBasic-description
${layout_selector} =  select#form-widgets-template_layout

${row_button_selector} =  a#btn-row
${column_button_selector} =  a#btn-column
${tile_button_selector} =  a#btn-tile
${row_drop_area_selector} =  div.layout
${column_drop_area_selector} =  div.cover-row
${tile_drop_area_selector} =  div.cover-column
${tile_cancel_area_selector} =  div.modal-backdrop
${delete_tile_selector} =  button.close
${CONTENT_CHOOSER_SELECTOR} =  div#contentchooser-content-search

*** Keywords ***

Start Browser and Autologin as
    [arguments]  ${role}

    Open Test Browser
    Enable Autologin as  $role

Start Browser and Log In as Site Owner
    Open Test Browser
    Log In As Site Owner
    Click Link  link=Home

Setup Cover Test Case
    Start Browser and Log In as Site Owner
    Go to Homepage

Click Add Cover
    Open Add New Menu
    Click Link  css=a#collective-cover-content
    Page Should Contain  Add Cover

Create Cover
    [arguments]  ${title}  ${description}  ${layout}=Empty layout

    Click Add Cover
    Input Text  css=${title_selector}  ${title}
    Input Text  css=${description_selector}  ${description}
    Select From List  css=${layout_selector}  ${layout}
    Click Button  Save
    Page Should Contain  Item created

Update
    [arguments]  ${title}  ${description}

    Click Link  link=Edit
    Input Text  css=${title_selector}  ${title}
    Input Text  css=${description_selector}  ${description}
    Click Button  Save
    Page Should Contain  Changes saved

Delete
    Open Action Menu
    Click Link  css=a#delete
    Click Button  Delete
    Page Should Contain  Plone site

Open Layout Tab
    [Documentation]  Click on Layout tab and wait until it loads.
    Click Link  link=Layout
    Wait Until Page Contains  Export layout
    Page Should Contain  Saved

Save Cover Layout
    [Documentation]  Click on Save button and wait until layout has been
    ...              saved.
    Page Should Contain  Save
    Click Element  css=a#btn-save.btn
    Wait Until Page Contains  Saved

Add Tile
    [arguments]  ${tile}

    Drag And Drop  xpath=//a[contains(@data-tile-type, ${tile})]  css=${tile_drop_area_selector}
    Wait Until Page Contains Element  css=.tile-name

Select Tile to Add
    [arguments]  ${tile}

    Click Element  xpath=//div[contains(@class, "tile-select-button") and contains(text(), ${tile})]

Delete Tile
    Wait Until Page Contains Element  css=${delete_tile_selector}
    Click Element  css=${delete_tile_selector}

Compose Cover
    [Documentation]  Click on Compose tab and wait until the layout has been
    ...              loaded.
    Wait Until Keyword Succeeds  5 sec  1 sec  Click Link  link=Compose
    Sleep  1s  Wait for cover compose to load
    Wait Until Page Contains Element  css=div#contentchooser-content-show-button
    Page Should Contain  Add Content

Open Content Chooser
    Click Element  css=div#contentchooser-content-show-button
    Wait Until Element Is Visible  css=${CONTENT_CHOOSER_SELECTOR}
