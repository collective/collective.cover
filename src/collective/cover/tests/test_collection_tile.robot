*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${collection_tile_location}  'collective.cover.collection'
${collection_selector}  .ui-draggable .contenttype-collection
${tile_selector}  div.tile-container div.tile
${title_field_id}  collective-cover-collection-header
${title_sample}  Some text for title
${title_other_sample}  This text should never be saved
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test Collection Tile
    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  My Cover  Description

    # add a collection tile to the layout
    Edit Cover Layout
    Page Should Contain  Export layout
    Add Tile  ${collection_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain  Please drop a collection here to fill the tile

    # drag&drop a Collection
    Open Content Chooser
    Drag And Drop  css=${collection_selector}  css=${tile_selector}
    Wait Until Page Contains  The collection doesn't have any results
    Page Should Contain  Go to related collection

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain  The collection doesn't have any results
    Page Should Not Contain  Go to related collection

    # edit the tile and check AJAX refresh
    Compose Cover
    # this is to demonstrate the bug mentioned above
    Page Should Contain  Go to related collection
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_sample}
    Click Button  Save
    Wait Until Page Contains  ${title_sample}

    # edit the tile but cancel operation
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_other_sample}
    Click Button  Cancel
    Wait Until Page Contains  ${title_sample}

    # change criteria for collection so it shows images
    Click Link  link=My collection
    Click Link  link=Edit
    Select From List  xpath=//select[@name="addindex"]  portal_type
    # deal with AJAX delays
    Wait Until Page Contains Element  xpath=//input[@value="Image"]
    Select Checkbox  xpath=//input[@value="Image"]
    Select From List  xpath=//select[@name="sort_on"]  getId
    Click Button  Save

    # collection tile has results
    Click Link  link=My Cover
    Page Should Not Contain  The collection doesn't have any results
    Page Should Contain  Test image

    # change header and title HTML tag
    Edit Cover Layout
    Click Element  css=a.config-tile-link
    Select From List  xpath=//select[@name="collective.cover.collection.header.htmltag"]  h3
    Select From List  xpath=//select[@name="collective.cover.collection.title.htmltag"]  h4
    Click Button  Save

    # title and item header should be same as the one configured above
    Compose Cover
    Element Text Should Be  css=.tile-header h3  Some text for title
    Element Text Should Be  css=.collection-item h4:first-child  Test image

    # delete the tile
    Edit Cover Layout
    Delete Tile
    Save Cover Layout
