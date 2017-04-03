*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${file_selector}  .ui-draggable .contenttype-file
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
    Page Should Contain  Recent items
    Page Should Contain  Content tree

    # make a search on Recent items
    Click Element  link=Recent items
    Input Text  css=#recent input  folder
    # FIXME: we have no result counter in here
    #Wait Until Page Contains  1 Results
    Click Element  css=#recent ${contentchooser_search_clear}

    Click Element  link=Content tree
    Wait Until Page Contains  Plone site

    # make a search on Content tree
    Input Text  css=#content-trees input  file
    Wait Until Page Contains  1 Results

    # navigate the tree
    Click Element  css=#content-trees ${contentchooser_search_clear}
    Input Text  css=#content-trees input  file
    Wait Until Page Contains  1 Results
    Page Should Contain Element  css=${file_selector}
    # TODO: Refactor this test before https://github.com/collective/collective.cover/issues/508
    # Click Element  css=${file_selector}
    # Wait Until Page Contains  My file

    # go back to tree root
    # Click Element  link=Plone site
    # ${TIMEOUT} =  Get Selenium timeout
    # ${IMPLICIT_WAIT} =  Get Selenium implicit wait
    # Wait Until Keyword Succeeds  ${TIMEOUT}  ${IMPLICIT_WAIT}
    # ...                          Page Should Not Contain  My file

    # Click Element  css=${contentchooser_close}
    # Wait Until Keyword Succeeds  ${TIMEOUT}  ${IMPLICIT_WAIT}
    # ...                          Element Should Not Be Visible  css=${CONTENT_CHOOSER_SELECTOR}
