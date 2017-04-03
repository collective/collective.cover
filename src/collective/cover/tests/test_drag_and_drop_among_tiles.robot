*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${banner_tile_location}  'collective.cover.banner'
${list_tile_location}  'collective.cover.list'
${carousel_tile_location}  'collective.cover.carousel'
${image_selector}  .ui-draggable .contenttype-image
${basic_tile_selector}  [data-tile-type=collective\\.cover\\.basic]
${banner_tile_selector}  [data-tile-type=collective\\.cover\\.banner]
${list_tile_selector}  [data-tile-type=collective\\.cover\\.list]

*** Test cases ***

Test Drag And Drop Among Tiles
    [Tags]  Expected Failure

    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add a Basic tile to the layout
    Open Layout Tab
    Add Tile  ${basic_tile_location}
    Add Tile  ${banner_tile_location}
    Add Tile  ${list_tile_location}
    Save Cover Layout

    # drag&drop an Image
    Compose Cover
    Open Content Chooser
    Drag And Drop  css=${image_selector}  css=${basic_tile_selector}
    Wait Until Page Contains Element  css=div.cover-basic-tile a img
    Drag And Drop  css=${basic_tile_selector}  css=${banner_tile_selector}
    Wait Until Page Contains Element  css=div.cover-banner-tile a img
    Drag And Drop  css=${banner_tile_selector}  css=${list_tile_selector}
    Wait Until Page Contains Element  css=div.cover-list-tile a img
    Drag And Drop  css=${list_tile_selector}  css=${banner_tile_selector}
    Wait Until Page Contains Element  css=div.cover-banner-tile a img
    Drag And Drop  css=${banner_tile_selector}  css=${basic_tile_selector}
    Wait Until Page Contains Element  css=div.cover-basic-tile a img

    Open Layout Tab
    Delete Tile
    Delete Tile
    Delete Tile
    Save Cover Layout
