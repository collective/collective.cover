*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${carousel_tile_location}  "collective.cover.carousel"
${document_selector}  //fieldset[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Document"]/span[text()='My document']/..
${image_selector}  //fieldset[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Image"]/span[text()='Test image']/..
${image_title}  //div[@class="galleria-info-title"]/a[text()='Test image']/..
${image_selector2}  //fieldset[@id="content-trees"]//li[@class="ui-draggable"]/a[@data-ct-type="Image"]/span[text()='Test image #1']/..
${image_title2}  //div[@class="galleria-info-title"]/a[text()='Test image #1']/..
${image_title_test}  //div[@class="galleria-info-title"]/a[text()='New Title']/..
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
    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add a carousel tile to the layout
    Open Layout Tab
    Add Tile  ${carousel_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain  This carousel is empty; open the content chooser and drag-and-drop some items here.

    # Test if we can edit the cover without any content added to it yet
    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Carousel Tile
    Click Button  Cancel

    # drag&drop an Image
    Open Content Chooser
    Click Element  link=Content tree
    Drag And Drop  xpath=${image_selector}  css=${tile_selector}

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

    # HACK: object not being added to tile when dropped; just, try again
    #       Galleria messing around the DOM?
    Drag And Drop  xpath=${image_selector2}  css=${tile_selector}

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

    # testing against Galleria is a PITA; slow down the process from here
    Set Selenium Speed  .5

    ### Test Custom Title functionality
    Click Link  link=View
    Wait Until Page Contains Element  xpath=${image_title}
    ${title} =  Get Text  xpath=.//div[@class='galleria-info-title']/a
    Should Be Equal  ${title}  Test image

    # Go to the right
    Click Element  xpath=.//div[@class='galleria-image-nav-right']
    Wait Until Page Contains Element  xpath=${image_title2}
    ${title} =  Get Text  xpath=.//div[@class='galleria-info-title']/a
    Should Be Equal  ${title}  Test image #1

    # Set custom Title
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Carousel Tile
    Input Text  xpath=.//div[contains(@class,"textline-sortable-element")][2]//input[@class='custom-title-input']  New Title
    Click Button  Save
    Sleep  2s  Wait for carousel to load

    Click Link  link=View
    Wait Until Page Contains Element  xpath=${image_title}
    ${title} =  Get Text  xpath=.//div[@class='galleria-info-title']/a
    Should Be Equal  ${title}  Test image

    # Go to the right
    Click Element  xpath=.//div[@class='galleria-image-nav-right']
    Wait Until Page Contains Element  xpath=${image_title_test}
    ${title} =  Get Text  xpath=.//div[@class='galleria-info-title']/a
    Should Be Equal  ${title}  New Title

    ### Test Custom Description functionality
    Click Link  link=View
    Wait Until Page Contains Element  xpath=${image_title}
    ${description} =  Get Text  xpath=.//div[@class='galleria-info-description']
    Should Be Equal  ${description}  This image was created for testing purposes

    # Go to the right
    Click Element  xpath=.//div[@class='galleria-image-nav-right']
    Wait Until Page Contains Element  xpath=${image_title_test}
    ${description} =  Get Text  xpath=.//div[@class='galleria-info-description']
    Should Be Equal  ${description}  This image #1 was created for testing purposes

    # Set custom Description
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Carousel Tile
    Input Text  xpath=.//div[contains(@class,"textline-sortable-element")][2]//textarea[@class='custom-description-input']  New Description
    Click Button  Save
    Sleep  2s  Wait for carousel to load

    Click Link  link=View
    Wait Until Page Contains Element  xpath=${image_title}
    ${description} =  Get Text  xpath=.//div[@class='galleria-info-description']
    Should Be Equal  ${description}  This image was created for testing purposes

    # Go to the right
    Click Element  xpath=.//div[@class='galleria-image-nav-right']
    Wait Until Page Contains Element  xpath=${image_title_test}
    ${description} =  Get Text  xpath=.//div[@class='galleria-info-description']
    Should Be Equal  ${description}  New Description

    ### Test Custom URL functionality
    Click Link  link=View
    Wait Until Page Contains Element  xpath=${image_title}
    ${image_url} =  Get Element Attribute  xpath=.//div[@class='galleria-info-title']/a@href
    Should Be Equal  ${image_url}  ${PLONE_URL}/my-image/view

    # Go to the right
    Click Element  xpath=.//div[@class='galleria-image-nav-right']
    Wait Until Page Contains Element  xpath=${image_title_test}
    ${image_url} =  Get Element Attribute  xpath=.//div[@class='galleria-info-title']/a@href
    Should Be Equal  ${image_url}  ${PLONE_URL}/my-image1/view

    # Set custom URL
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Carousel Tile
    Input Text  xpath=.//div[contains(@class,"textline-sortable-element")][2]//input[@class='custom-url-input']  http://www.google.com
    Click Button  Save
    Sleep  2s  Wait for carousel to load

    Click Link  link=View
    Wait Until Page Contains Element  xpath=${image_title}
    ${image_url} =  Get Element Attribute  xpath=.//div[@class='galleria-info-title']/a@href
    Should Be Equal  ${image_url}  ${PLONE_URL}/my-image/view

    # Go to the right
    Click Element  xpath=.//div[@class='galleria-image-nav-right']
    Wait Until Page Contains Element  xpath=${image_title_test}
    ${image_url} =  Get Element Attribute  xpath=.//div[@class='galleria-info-title']/a@href
    Should Be Equal  ${image_url}  http://www.google.com/

    # delete the tile
    Open Layout Tab
    Delete Tile
    Save Cover Layout
