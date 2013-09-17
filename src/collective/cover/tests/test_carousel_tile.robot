*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${carousel_tile_location}  "collective.cover.carousel"
${image_selector}  .ui-draggable .contenttype-image:nth-child(1)
${image_selector2}  .ui-draggable .contenttype-image:nth-child(2)
${tile_selector}  div.tile-container div.tile
${autoplay_id}  collective-cover-carousel-autoplay-0
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test Carousel Tile
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description  Empty layout
    Click Link  link=Layout

    Add Tile  ${carousel_tile_location}
    Save Cover Layout

    Click Link  link=Compose

    Page Should Contain  Galleria.configure({ autoplay: true });

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Page Should Contain  Test image
    Page Should Contain  This image was created for testing purposes

    Drag And Drop  css=${image_selector2}  css=${tile_selector}
    #Xpath Should Match X Times  //div[contains(@class, 'galleria-image')]  2

    Click Link  css=${edit_link_selector}
    Page Should Contain Element  css=.textline-sortable-element
    Unselect Checkbox  ${autoplay_id}
    Click Button  Save
    Wait Until Page Contains  Galleria.configure({ autoplay: false });

    #Xpath Should Match X Times  //div[contains(@class, 'textline-sortable-element')]  2

    Click Link  link=Layout
    Delete Tile
    Save Cover Layout
