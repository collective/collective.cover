*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote
Library  ${CURDIR}/TestInternalServerError.py

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${basic_tile_location}  'collective.cover.basic'
${title_field_id}  collective-cover-basic-title
${title_sample}  Some text for title
${edit_link_selector}  a.edit-tile-link

*** Test cases ***

Test Purge Data
    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add tile to the layout
    Open Layout Tab
    Add Tile  ${basic_tile_location}
    Save Cover Layout

    # go to compose view and edit the tile
    Compose Cover

    # keep edit url and compose url for later use
    ${compose_url} =  Get Location
    ${edit_url} =  Get Element Attribute  css=${edit_link_selector}@href

    Click Link  css=${edit_link_selector}
    Wait Until Page Contains  Edit Basic Tile
    Input Text  id=${title_field_id}  ${title_sample}
    Click Button  Save

    # check for successful AJAX refresh
    Wait Until Page Contains  ${title_sample}

    Go to  ${compose_url}
    Open Layout Tab
    Delete Tile
    Save Cover Layout

    # confirm that data is gone
    Go to  ${edit_url}
    ${value} =  Get value  ${title_field_id}
    Should be equal  ${EMPTY}  ${value}
