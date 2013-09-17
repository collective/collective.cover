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
    Click Link  link=Layout

    Add Tile  ${collection_tile_location}
    Save Cover Layout

    Click Link  link=Compose
    Page Should Contain  Please drop a collection here to fill the tile

    Click Element  css=div#contentchooser-content-show-button

    Drag And Drop  css=${collection_selector}  css=${tile_selector}
    Page Should Contain  The collection doesn't have any results

    # go back to compose view to edit header
    Click Link  link=Compose
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_sample}
    # before saving, clean the banner tile to make sure it has been loaded
    # with the new text
    Execute Javascript  $('.tile').empty()
    Click Button  Save
    # save via ajax => wait until the tile has been reloaded
    Wait Until Page Contains  ${title_sample}

    # edit tile but don't save it
    Click Link  css=${edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${title_other_sample}
    Click Button  Cancel
    Page Should Not Contain  ${title_other_sample}
    Page Should Contain  ${title_sample}

    Click Link  My collection
    Workflow Make Private

    # log out to check collection tile doesn't show anything to anonymous user
    # we can't use 'Log out' as we logged in automatically
    # log out from Zope
    Go to  ${PLONE_URL}//@@plone-root-logout
    Click Button  Cancel

    Click Link  Title
    Page Should Not Contain  The collection doesn't have any results
    And Page Should Not Contain  Forgot your password?

    Log In As Site Owner
    Go to Homepage
    Click Link  My collection
    Workflow Promote to Draft

    Click Link  Title
    Click Link  link=Layout
    Delete Tile
    Save Cover Layout
