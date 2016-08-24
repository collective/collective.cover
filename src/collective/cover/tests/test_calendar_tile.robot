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
    ...    var $next = jQuery('a.calendarNext');
    ...    var str_klasses = $next.attr('class');
    ...    if (str_klasses.indexOf('kssattr') >= 0) {
    ...      var klasses = str_klasses.split(' ');
    ...      var i, klass, len, year, year_check;
    ...      for (i = 0, len = klasses.length; i < len; i++) {
    ...        klass = klasses[i];
    ...        year_check = 'kssattr-year-';
    ...        if (klass.indexOf(year_check) === 0) {
    ...          return klass.slice(year_check.length);
    ...        }
    ...      }
    ...    }
    ...    return $next.attr('data-year');
    ...  })();
    ${nextmonth} =  Execute Javascript
    ...  return (function() {
    ...    var $next = jQuery('a.calendarNext');
    ...    var str_klasses = $next.attr('class');
    ...    if (str_klasses.indexOf('kssattr') >= 0) {
    ...      var klasses = str_klasses.split(' ');
    ...      var i, klass, len, month, month_check;
    ...      for (i = 0, len = klasses.length; i < len; i++) {
    ...        klass = klasses[i];
    ...        month_check = 'kssattr-month-';
    ...        if (klass.indexOf(month_check) === 0) {
    ...          return klass.slice(month_check.length);
    ...        }
    ...      }
    ...    }
    ...    return $next.attr('data-month');
    ...  })();
    Wait Until Keyword Succeeds  5 sec  1 sec  Click Link  css=a.calendarNext
    Wait Until Keyword Succeeds  5 sec  1 sec  Click Link  css=a.calendarNext
    Page Should Contain Element  jquery=a.calendarPrevious[data-month=${nextmonth}][data-year=${nextyear}],a.calendarPrevious.kssattr-month-${nextmonth}.kssattr-year-${nextyear}
    Wait Until Keyword Succeeds  5 sec  1 sec  Click Link  css=a.calendarPrevious
    Wait Until Keyword Succeeds  5 sec  1 sec  Click Link  css=a.calendarPrevious
    Page Should Contain Element  jquery=a.calendarNext[data-month=${nextmonth}][data-year=${nextyear}],a.calendarNext.kssattr-month-${nextmonth}.kssattr-year-${nextyear}

    # delete the tile
    Open Layout Tab
    Delete Tile
    Save Cover Layout
