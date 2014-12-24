*** Settings ***

Documentation  https://github.com/collective/collective.cover/issues/59

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'

*** Test cases ***

Test Reverse Proxy
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  Title  Description
    Edit Cover Layout

    Add Tile  ${basic_tile_location}
    Save Cover Layout

    Click Link  link=View
    Page Should Not Contain  Please drag&drop some content here to populate the tile.

    Compose Cover
    Page Should Contain   Please drag&drop some content here to populate the tile.

    Open Browser  http://localhost:${PORT}/VirtualHostBase/http/127.0.0.1:${PORT}/plone/VirtualHostRoot/_vh_subplone/title-1
    Page Should Not Contain   Please drag&drop some content here to populate the tile.

    Switch Browser  1
    Edit Cover Layout
    Delete Tile
    Save Cover Layout

    Switch Browser  2
    Close Browser
