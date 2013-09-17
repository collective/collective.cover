*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${folder_selector}  .contenttype-folder
${input_contenttree}  contentchooser-content-trees
${tile_selector}  div.tile-container div.tile
${path_selector}  div#content-trees div#internalpath

*** Test cases ***

# TODO: mix with test_contentchooser_tree_tab.robot
Test Content Chooser Tree Tab Path
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description  Empty layout
    Click Link  link=Layout

    Add Tile  ${basic_tile_location}
    Save Cover Layout

    # Test navigate tree
    #
    Click Link  link=Compose
    Page Should Contain   Please drag&drop some content here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button

    Click Element  link=Content tree

    Page Should Contain Element  css=${folder_selector}
    Click Element  css=${folder_selector}

    Page Should Contain Element  css=${path_selector}
    Wait Until Page Contains Element  css=div#content-trees div#internalpath a
    Page Should Contain  Plone site → my-folder

    # Test searches
    Click Link  link=Compose
    Page Should Contain   Please drag&drop some content here to populate the tile.

    Click Element  css=div#contentchooser-content-show-button

    Click Element  link=Content tree
    # XXX: filtering code use some slow fadeOut code, we must slow down selenium
    Input text  name=${input_contenttree}  folder
    Wait Until Page Contains  1 Results

    Page Should Contain Element  css=${folder_selector}
    Click Element  css=${folder_selector}

    Page Should Contain Element  css=${path_selector}
    Wait Until Page Contains Element  css=div#content-trees div#internalpath a
    Page Should Contain  Plone site → my-folder

    Input text  name=${input_contenttree}  foo-bar
    Page Should Contain  0 Results

# Changed in the new UI
#    Click Element  css=#home a
#
#    Page Should Contain Element  css=${folder_selector}
#    Click Element  css=${folder_selector}

    Page Should Contain Element  css=${path_selector}
    Wait Until Page Contains Element  css=div#content-trees div#internalpath a
    Page Should Contain  Plone site → my-folder
