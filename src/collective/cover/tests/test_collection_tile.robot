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
    Create Cover  Title  Description  Empty layout

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
    # FIXME: there is a bug here as the first time this message is not shown
    #Page Should Contain  Go to related collection
    Page Should Not Contain  Go to related collection

    # TODO: test with a non-empty collection

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

    # delete the tile
    Edit Cover Layout
    Delete Tile
    Save Cover Layout
