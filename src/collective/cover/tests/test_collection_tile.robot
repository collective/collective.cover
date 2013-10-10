*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

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
    Click Link  link=Layout
    Page Should Contain  Export layout
    Add Tile  ${collection_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Click Link  link=Compose
    Page Should Contain  Please drop a collection here to fill the tile

    # drag&drop a Collection
    Open Content Chooser
    Drag And Drop  css=${collection_selector}  css=${tile_selector}
    Wait Until Page Contains  The collection doesn't have any results

    # TODO: test with a non-empty collection

    # edit the tile and check AJAX refresh
    Click Link  link=Compose
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_sample}
    Click Button  Save
    Wait Until Page Contains  ${title_sample}

    # edit the tile but cancel operation
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_other_sample}
    Click Button  Cancel
    Wait Until Page Contains  ${title_sample}

    # delete the tile
    Click Link  link=Layout
    Delete Tile
    Save Cover Layout
