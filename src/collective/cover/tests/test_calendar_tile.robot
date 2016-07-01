*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

# XXX: test is randomly failing under Plone 4.2 only
Default Tags  Mandelbug

*** Variables ***

${calendar_tile_location}  'collective.cover.calendar'

*** Test cases ***

Test Calendar Tile
    # XXX: test is randomly failing under Plone 4.2 only
    Run keyword if  '${CMFPLONE_VERSION}' >= '4.3'  Remove Tags  Mandelbug

    Enable Autologin as  Site Administrator
    Go to Homepage
    Create Cover  Title  Description

    # add tile to the layout
    Open Layout Tab
    Add Tile  ${calendar_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain  Calendar Tile

    # test next / prev buttons
    ${nextyear} =  Execute Javascript
    ...  return (function() {
    ...    var $next = jQuery('a.calendar-tile-next');
    ...    return $next.attr('data-year');
    ...  })();
    ${nextmonth} =  Execute Javascript
    ...  return (function() {
    ...    var $next = jQuery('a.calendar-tile-next');
    ...    return $next.attr('data-month');
    ...  })();
    Wait Until Keyword Succeeds  5 sec  1 sec  Click Link  css=a.calendar-tile-next
    Wait Until Keyword Succeeds  5 sec  1 sec  Click Link  css=a.calendar-tile-next
    Page Should Contain Element  xpath=.//a[@class='calendar-tile-prev'][@data-month='${nextmonth}'][@data-year='${nextyear}']
    Wait Until Keyword Succeeds  5 sec  1 sec  Click Link  css=a.calendar-tile-prev
    Wait Until Keyword Succeeds  5 sec  1 sec  Click Link  css=a.calendar-tile-prev
    Page Should Contain Element  xpath=.//a[@class='calendar-tile-next'][@data-month='${nextmonth}'][@data-year='${nextyear}']

    # delete the tile
    Open Layout Tab
    Delete Tile
    Save Cover Layout
