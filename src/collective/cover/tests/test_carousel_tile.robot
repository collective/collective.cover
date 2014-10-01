*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${carousel_tile_location}  "collective.cover.carousel"
${document_selector}  //div[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Document"]/span[text()='My document']/..
${image_selector1}  //div[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Image"]/span[text()='my-image1']/..
${image_selector2}  //div[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Image"]/span[text()='my-image2']/..
${tile_selector}  div.tile-container div.tile
${autoplay_id}  collective-cover-carousel-autoplay-0
${edit_link_selector}  a.edit-tile-link

*** Keywords ***

Get Total Carousel Images
    [Documentation]  Total number of images in carousel is stored in this
    ...              element
    # Note: we are a bit lazy about adding concat here, but then how long do you want this line to be?
    ${return} =  Get Matching XPath Count  //div[contains(@class,"cycle2-carousel")]//div[contains(concat(" ", @class," "), " slide ") and not(contains(@class, "sentinel"))]
    [Return]  ${return}

*** Test cases ***

Test Carousel Tile
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
    Click Element  link=Content tree
    Drag And Drop  xpath=${image_selector1}  css=${tile_selector}
    # The carousel was previously empty, so autoplay=false, so we might not see the carousel updated
    # Wait Until Page Contains  Test image #1
    # Page Should Contain  This image was created for testing purposes

    # move to the default view and check tile persisted
    Click Link  link=View
    Wait Until Page Contains  Test image #1
    Page Should Contain  This image #1 was created for testing purposes
    # we have 1 image in the carousel
    ${images} =  Get Total Carousel Images
    Should Be Equal  '${images}'  '1'

    # drag&drop another Image
    Compose Cover
    Sleep  1s  Wait for carousel to load
    Open Content Chooser
    Click Element  link=Content tree

    Drag And Drop  xpath=${image_selector2}  css=${tile_selector}
    # Need to change view before second image is loaded

    # move to the default view and check tile persisted
    Click Link  link=View
    Sleep  5s  Wait for carousel to load
    Wait Until Page Contains  Test image #2
    Page Should Contain  This image #2 was created for testing purposes
    # we now have 2 images in the carousel
    ${images} =  Get Total Carousel Images
    Should Be Equal  '${images}'  '2'

    # drag&drop an object without an image: a Page
    Compose Cover
    Sleep  1s  Wait for carousel to load
    Open Content Chooser
    Click Element  link=Content tree

    Drag And Drop  xpath=${document_selector}  css=${tile_selector}

    # Documents are (at least slightly) revived in Carousel thanks to Cycle2
    Click Link  link=View
    Wait Until Page Contains  My document
    Page Should Contain  This document was created for testing purposes

    # carousel autoplay is enabled
    Page Should Contain Element  xpath=//div[contains(@class,"cycle2-carousel") and @data-cycle-paused="false"]

    # edit the tile
    Compose Cover
    Click Link  css=${edit_link_selector}
    Page Should Contain Element  css=.textline-sortable-element
    # disable carousel autoplay
    Unselect Checkbox  ${autoplay_id}
    Click Button  Save
    Wait Until Page Contains  Test image #1
    Page Should Contain  This image #1 was created for testing purposes

    # carousel autoplay is now disabled. Sometimes we need to reload the page.
    Reload Page
    Page Should Contain Element  xpath=//div[contains(@class,"cycle2-carousel") and @data-cycle-paused="true"]

    # delete the tile
    Edit Cover Layout
    Delete Tile
    Save Cover Layout
