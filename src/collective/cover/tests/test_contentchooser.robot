*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${file_selector}  .ui-draggable .contenttype-file
${document_selector}  a[title="This document was created for testing purposes : /my-document"]
${folder_selector}  a[title="This folder was created for testing purposes"]
${contentchooser_search_selector}  FIXME
${contentchooser_search_clear}  a.contentchooser-clear
${contentchooser_close}  div.close
${tile_selector}  div.tile-container div.tile

*** Test cases ***

Test Content Chooser
    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add a Basic tile to the layout
    Open Layout Tab
    Add Tile  ${basic_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain  Please drag&drop some content here to populate the tile.

    # Content Chooser should contain 2 tabs
    Open Content Chooser
    Page Should Contain  Recent Items
    Page Should Contain  Content Tree

    # make a search on Recent Items
    Click Element  link=Recent Items
    Input Text  css=#recent input  My file
    Wait Until Page Contains  1 Results
    Click Element  css=#recent ${contentchooser_search_clear}
    Page Should Not Contain  1 Results
    Page Should Contain Element  css=${document_selector}

    Click Element  link=Content Tree
    Wait Until Page Contains  Plone site

    # make a search on Content Tree
    Input Text  css=#content-trees input  file
    Wait Until Page Contains  1 Results

    # navigate the tree
    Click Element  css=#content-trees ${contentchooser_search_clear}
    Page Should Not Contain  1 Results
    Page Should Contain Element  css=${document_selector}
    Input Text  css=#content-trees input  My folder
    Wait Until Page Contains  1 Results
    Page Should Contain Element  css=${folder_selector}
    Click Element  css=${folder_selector}
    Page Should Contain  Plone site → My folder
    Page Should Not Contain Element  css=${folder_selector}
    Click link  Plone site
    Page Should Contain Element  css=${folder_selector}
