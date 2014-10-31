*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${carousel_tile_location}  "collective.cover.carousel"
${document_selector}  //div[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Document"]/span[text()='My document']/..
${image_selector}  //div[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Image"]/span[text()='Test image']/..
${image_title}  //div[@class="galleria-info-title"]/a[text()='Test image']/..
${image_selector2}  //div[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Image"]/span[text()='Test image #1']/..
${image_title2}  //div[@class="galleria-info-title"]/a[text()='Test image #1']/..
${tile_selector}  div.tile-container div.tile
${autoplay_id}  collective-cover-carousel-autoplay-0
${edit_link_selector}  a.edit-tile-link

*** Keywords ***

Get Total Carousel Images
    [Documentation]  Total number of images in carousel is stored in this
    ...              element
    ${return} =  Get Element Attribute  xpath=//div[@class="galleria-stage"]/div[@class="galleria-counter"]/span[@class="galleria-total"]@innerHTML
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
    Drag And Drop  xpath=${image_selector}  css=${tile_selector}
    # The carousel was previously empty, so autoplay=false, so we might not see the carousel updated
    # Wait Until Page Contains  Test image
    # Page Should Contain  This image was created for testing purposes

    # move to the default view and check tile persisted
    Click Link  link=View
    # Wait Until Page Contains would always work because of the top navigation
    Wait Until Page Contains Element  xpath=${image_title}
    Page Should Contain  This image was created for testing purposes
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
    # Wait Until Page Contains would always work because of the top navigation
    Wait Until Page Contains Element  xpath=${image_title2}
    Page Should Contain  This image #1 was created for testing purposes
    # we now have 2 images in the carousel
    ${images} =  Get Total Carousel Images
    Should Be Equal  '${images}'  '2'

    # drag&drop an object without an image: a Page
    Compose Cover
    Sleep  1s  Wait for carousel to load
    Open Content Chooser
    Click Element  link=Content tree

    Drag And Drop  xpath=${document_selector}  css=${tile_selector}

    Click Link  link=View
    # We should still have 2 images in the carousel
    ${images} =  Get Total Carousel Images
    Should Be Equal  '${images}'  '2'

    # carousel autoplay is enabled
    Page Should Contain  options.autoplay = true;

    # edit the tile
    Compose Cover
    Click Link  css=${edit_link_selector}
    Page Should Contain Element  css=.textline-sortable-element
    # disable carousel autoplay
    Unselect Checkbox  ${autoplay_id}
    Click Button  Save
    Wait Until Page Contains  Test image
    Page Should Contain  This image was created for testing purposes

    # carousel autoplay is now disabled. Sometimes we need to reload the page.
    Compose Cover
    Page Should Contain  options.autoplay = false;

    # Test Custom URL functionality
    Click Link  link=View
    ${image_url} =  Get Element Attribute  xpath=.//div[@class='galleria-info-title']/a@href
    Should Be Equal  ${image_url}  ${PLONE_URL}/my-image/view

    # Go to the right
    Click Element  xpath=.//div[@class='galleria-image-nav-right']
    Wait Until Page Contains Element  xpath=${image_title2}
    ${image_url} =  Get Element Attribute  xpath=.//div[@class='galleria-info-title']/a@href
    Should Be Equal  ${image_url}  ${PLONE_URL}/my-image1/view


    Compose Cover
    Click Link  css=${edit_link_selector}
    Input Text  xpath=.//div[@class='textline-sortable-element'][2]/input  http://www.google.com
    Click Button  Save
    Sleep  2s  Wait for carousel to load

    Click Link  link=View
    ${image_url} =  Get Element Attribute  xpath=.//div[@class='galleria-info-title']/a@href
    Should Be Equal  ${image_url}  ${PLONE_URL}/my-image/view

    # Go to the right
    Click Element  xpath=.//div[@class='galleria-image-nav-right']
    Wait Until Page Contains Element  xpath=${image_title2}
    ${image_url} =  Get Element Attribute  xpath=.//div[@class='galleria-info-title']/a@href
    Should Be Equal  ${image_url}  http://www.google.com/

    # delete the tile
    Edit Cover Layout
    Delete Tile
    Save Cover Layout
