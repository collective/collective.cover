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

    # add a carousel tile to the layout
    Edit Cover Layout
    Add Tile  ${carousel_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    # FIXME: default message for empty tile
    Page Should Contain  Galleria.configure({ autoplay: true });

    # drag&drop an Image
    Open Content Chooser
    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Wait Until Page Contains  Test image
    Page Should Contain  This image was created for testing purposes

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  Test image

    # drag&drop another Image
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${image_selector2}  css=${tile_selector}
    # FIXME
    #Xpath Should Match X Times  //div[contains(@class, 'galleria-image')]  2

    # edit the tile
    Click Link  css=${edit_link_selector}
    Page Should Contain Element  css=.textline-sortable-element
    Unselect Checkbox  ${autoplay_id}
    Click Button  Save
    Wait Until Page Contains  Galleria.configure({ autoplay: false });
    # FIXME
    #Xpath Should Match X Times  //div[contains(@class, 'textline-sortable-element')]  2

    # delete the tile
    Edit Cover Layout
    Delete Tile
    Save Cover Layout
