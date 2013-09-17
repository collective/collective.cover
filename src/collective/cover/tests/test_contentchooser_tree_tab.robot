*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${document_selector}  .ui-draggable .contenttype-document
${folder_selector}  .ui-draggable .contenttype-folder
${input_contenttree}  contentchooser-content-trees
${contentchooser-content-show-button}  div#contentchooser-content-show-button
${home_contentchooser}  #home
${tile_selector}  div.tile-container div.tile

*** Test cases ***

Test Content Chooser Tree Tab
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description  Empty layout
    Click Link  link=Layout

    Add Tile  ${basic_tile_location}
    Save Cover Layout

    Click Link  link=Compose
    Page Should Contain   Please drag&drop some content here to populate the tile.

    Click Element  css=${contentchooser-content-show-button}

    Click Element  link=Content tree

    Drag And Drop  css=${document_selector}  css=${tile_selector}
    Page Should Contain  My document

    Input text  name=${input_contenttree}  front
    Wait Until Page Contains  1 Results
