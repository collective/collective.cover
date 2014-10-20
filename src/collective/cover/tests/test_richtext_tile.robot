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
    Edit Cover Layout

    Add Tile  ${tile_location}
    Save Cover Layout

    Compose Cover
    Page Should Contain  Please edit the tile to enter some text.

    # edit tile but don't save it
    Click Link  css=${edit_link_selector}
    Wait For Condition  return typeof tinyMCE != "undefined" && tinyMCE.activeEditor != null
    Execute Javascript  tinyMCE.activeEditor.setContent("${text_sample}");
    Click Button  Save
    # save via ajax => wait until the tile has been reloaded
    Wait Until Page Contains  ${text_sample}
    Page Should Contain  ${text_sample}

    # Go to view and check it's there
    Click Link  link=View
    Page Should Contain  ${text_sample}


    # Compose and don't save some other text
    Compose Cover
    Click Link  css=${edit_link_selector}
    Wait For Condition  return typeof tinyMCE != "undefined" && tinyMCE.activeEditor != null
    Execute Javascript  tinyMCE.activeEditor.setContent("${text_other_sample}");
    Click Button  Cancel
    Page Should Not Contain  ${text_other_sample}
    Page Should Contain  ${text_sample}

    Edit Cover Layout
    Delete Tile
    Save Cover Layout
