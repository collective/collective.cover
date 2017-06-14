*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${collection_tile_location}  'collective.cover.collection'
${collection_selector}  .ui-draggable .contenttype-collection
${tile_selector}  div.tile-container div.tile
${tile_header_selector}  div.tile-header h2
${title_field_id}  collective-cover-collection-header
${title}  Mandelbrot set
${title_alternate}  An alternate title for the tile
${edit_link_selector}  a.edit-tile-link
${no_results_msg}  The collection doesn't have any results
${related_msg}  Go to related collection
${more_msg}  More?

*** Test cases ***

Test Collection Tile
    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  My Cover  Description

    # add a collection tile to the layout
    Open Layout Tab
    Add Tile  ${collection_tile_location}
    Save Cover Layout

    Compose Cover
    # tile is empty, we must see default message
    Page Should Contain  Please drop a collection here to fill the tile

    # drag and drop a collection
    Open Content Chooser
    Drag And Drop  css=${collection_selector}  css=${tile_selector}
    # check tile is properly populated
    Wait Until Element Contains  css=${tile_header_selector}  ${title}
    Page Should Contain  Test image
    Page Should Contain  This image was created for testing purposes
    Page Should Contain Link  ${more_msg}
    Page Should Contain Link  ${related_msg}
    Page Should Not Contain  ${no_results_msg}

    # move to the default view
    Click Link  link=View
    # check information persisted
    Wait Until Element Contains  css=${tile_header_selector}  ${title}
    Page Should Contain  Test image
    Page Should Contain  This image was created for testing purposes
    Page Should Contain Link  ${more_msg}
    Page Should Not Contain Link  ${related_msg}
    Page Should Not Contain  ${no_results_msg}

    # go back to compose view and edit the tile
    Compose Cover
    Wait Until Element Contains  css=${tile_header_selector}  ${title}
    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Collection Tile
    Input Text  id=${title_field_id}  ${title_alternate}
    Click Button  Save
    Wait Until Page Does Not Contain  Edit Collection Tile

    # check for successful AJAX refresh
    Wait Until Page Contains  ${title_alternate}

    # change header and title HTML tag
    Open Layout Tab
    Click Element  css=a.config-tile-link
    Wait Until Page Contains  Configure Collection Tile
    Select From List  xpath=//select[@name="collective.cover.collection.header.htmltag"]  h1
    Select From List  xpath=//select[@name="collective.cover.collection.title.htmltag"]  h4
    Click Button  Save

    # title and item header should be same as the one configured above
    Compose Cover
    Element Text Should Be  css=.tile-header h1  ${title_alternate}
    Element Text Should Be  css=.collection-item h4:first-child  Test image

    # delete the tile
    Open Layout Tab
    Delete Tile
    Save Cover Layout
