*** Settings ***

Documentation  https://github.com/collective/collective.cover/issues/59

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'

*** Test cases ***

Test Reverse Proxy
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description
    Open Layout Tab

    Add Tile  ${basic_tile_location}
    Save Cover Layout

    Click Link  link=View
    Page Should Not Contain  Please drag&drop some content here to populate the tile.

    Compose Cover
    Page Should Contain   Please drag&drop some content here to populate the tile.

    Open Browser  http://localhost:${ZOPE_PORT}/VirtualHostBase/http/127.0.0.1:${ZOPE_PORT}/plone/VirtualHostRoot/_vh_subplone/title-1
    Page Should Not Contain   Please drag&drop some content here to populate the tile.

    Switch Browser  1
    Open Layout Tab
    Delete Tile
    Save Cover Layout

    Switch Browser  2
    Close Browser
