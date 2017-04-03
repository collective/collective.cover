*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${tile_location}  'collective.cover.richtext'
${text_sample}  Some text for title
${text_other_sample}  This text should never be saved
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test RichText Tile
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description
    Open Layout Tab

    Add Tile  ${tile_location}
    Save Cover Layout

    Compose Cover
    Page Should Contain  Please edit the tile to enter some text.

    # edit tile but don't save it
    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Rich Text Tile
    Sleep  1s  Wait for TinyMCE to load
    Wait For Condition  return typeof tinyMCE !== "undefined" && tinyMCE.activeEditor !== null && document.getElementById(tinyMCE.activeEditor.id) !== null
    Click Button  Cancel
    Wait Until Page Does Not Contain  Edit Rich Text Tile

    # check if TinyMCE loads a second time and edit the tile
    # see: https://github.com/collective/collective.cover/issues/543
    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Rich Text Tile
    Sleep  1s  Wait for TinyMCE to load
    Wait For Condition  return typeof tinyMCE !== "undefined" && tinyMCE.activeEditor !== null && document.getElementById(tinyMCE.activeEditor.id) !== null
    Execute Javascript  tinyMCE.activeEditor.setContent("${text_sample}");
    Click Button  Save
    # save via ajax => wait until the tile has been reloaded
    Wait Until Page Does Not Contain  Edit Rich Text Tile
    # check for successful AJAX refresh
    Wait Until Page Contains  ${text_sample}

    # Go to view and check it's there
    Click Link  link=View
    Page Should Contain  ${text_sample}

    Open Layout Tab
    Delete Tile
    Save Cover Layout
