*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${folder_selector}  .ui-draggable .contenttype-folder
${contentchooser_search_selector}  FIXME
${contentchooser_search_clear}  a.contentchooser-clear
${contentchooser_close}  div.close
${tile_selector}  div.tile-container div.tile

*** Test cases ***

Test Content Chooser
    [Tags]  Expected Failure

    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add a Basic tile to the layout
    Edit Cover Layout
    Page Should Contain  Export layout
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
    Input Text  css=#content-trees input  folder
    Wait Until Page Contains  1 Results
    Click Element  css=#content-trees ${contentchooser_search_clear}

    # navigate the tree
    Input Text  css=#content-trees input  folder
    Wait Until Page Contains  1 Results
    Page Should Contain Element  css=${folder_selector}
    Click Element  css=${folder_selector}
    Wait Until Page Contains  Plone site → my-folder

    # go back to tree root
    Click Element  link=Plone site
    ${TIMEOUT} =  Get Selenium timeout
    ${IMPLICIT_WAIT} =  Get Selenium implicit wait
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${IMPLICIT_WAIT}
    ...                          Page Should Not Contain  Plone site → my-folder

    Click Element  css=${contentchooser_close}
    Wait Until Keyword Succeeds  ${TIMEOUT}  ${IMPLICIT_WAIT}
    ...                          Element Should Not Be Visible  css=${CONTENT_CHOOSER_SELECTOR}

