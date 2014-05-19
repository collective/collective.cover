*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${carousel_tile_location}  "collective.cover.carousel"
${document_selector}  .ui-draggable .contenttype-document
${image_selector}  .ui-draggable .contenttype-image:nth-child(1)
${image_selector2}  .ui-draggable .contenttype-image:nth-child(2)
${tile_selector}  div.tile-container div.tile
${autoplay_id}  collective-cover-carousel-autoplay-0
${edit_link_selector}  a.edit-tile-link

*** Keywords ***

Get Total Carousel Images
    [Documentation]  Total number of images in carousel is stored in this
    ...              element (FIXME: keyword is returning an empty string)
    ${return} =  Get Text  css=span.galleria-total
    [Return]  ${return}

*** Test cases ***

Test Carousel Tile
    # FIXME: https://github.com/collective/collective.cover/issues/378
    [Tags]  Expected Failure

    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add a carousel tile to the layout
    Edit Cover Layout
    Add Tile  ${carousel_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain  This carousel is empty; open the content chooser and drag-and-drop some items here.

    # drag&drop an Image
    Open Content Chooser
    Drag And Drop  css=${image_selector}  css=${tile_selector}
    Wait Until Page Contains  Test image
    Wait Until Page Contains  This image was created for testing purposes
    # we have 1 image in the carousel
    #${images} =  Get Total Carousel Images
    #Should Be Equal  '${images}'  '1'

    # move to the default view and check tile persisted
    Click Link  link=View
    Wait Until Page Contains  Test image
    Wait Until Page Contains  This image was created for testing purposes

    # drag&drop another Image
    Compose Cover
    Sleep  1s  Wait for carousel to load
    Open Content Chooser
    Click Element  link=Content tree

    Drag And Drop  css=${document_selector}  css=${tile_selector}
    Wait Until Page Contains  Test image
    Wait Until Page Contains  This image was created for testing purposes
    # we now have 2 images in the carousel
    #${images} =  Get Total Carousel Images
    #Should Be Equal  '${images}'  '2'

    # move to the default view and check tile persisted
    Click Link  link=View
    Sleep  5s  Wait for carousel to load
    #Wait Until Page Contains  Test image
    #Page Should Contain  This image was created for testing purposes

    # drag&drop an object without an image: a Page
    Compose Cover
    Sleep  1s  Wait for carousel to load
    Open Content Chooser
    Click Element  link=Content tree

    Drag And Drop  css=${document_selector}  css=${tile_selector}

    # move to the default view and check tile persisted
    Click Link  link=View
    Wait Until Page Contains  My document
    Page Should Contain  This document was created for testing purposes

    # carousel autoplay is enabled
    Page Should Contain  Galleria.configure({ autoplay: true });

    # edit the tile
    Click Link  css=${edit_link_selector}
    Page Should Contain Element  css=.textline-sortable-element
    # disable carousel autoplay
    Unselect Checkbox  ${autoplay_id}
    Click Button  Save
    Wait Until Page Contains  Test image
    Wait Until Page Contains  This image was created for testing purposes

    # carousel autoplay is now disabled. Sometimes we need to reload the page.
    Compose Cover
    Page Should Contain  Galleria.configure({ autoplay: false });

    # delete the tile
    Edit Cover Layout
    Delete Tile
    Save Cover Layout
