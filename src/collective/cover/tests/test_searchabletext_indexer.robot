*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${tile_location}  'collective.cover.richtext'
${title}  Törkylempijävongahdus
${description}  Albert osti fagotin ja töräytti puhkuvan melodian.
${text}  Fahrenheit ja Celsius yrjösivät Åsan backgammon-peliin, Volkswagenissa, daiquirin ja ZX81:n yhteisvaikutuksesta.
${edit_link_selector}  css=a.edit-tile-link
${search_field_selector}  id=searchGadget
${search_button_selector}  css=.searchButton
@{search_words}  torkylempijavongahdus  Törkylempijävongahdus  töräytti  Fahrenheit  Åsan
${search_results_number_selector}  xpath=//strong[@id='search-results-number']

*** Test cases ***

Test RichText Tile is Searchable
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  ${title}  ${description}
    Edit Cover Layout
    Add Tile  ${tile_location}
    Save Cover Layout

    # Add the text to the richtext tile
    Compose Cover
    Click Link  ${edit_link_selector}
    Wait For Condition  return typeof tinyMCE != "undefined" && tinyMCE.activeEditor != null
    Execute Javascript  tinyMCE.activeEditor.setContent("${text}");
    Click Button  Save
    Wait Until Page Contains  ${text}

    # Make a number of searches to verify the index
    : FOR  ${word}  IN  @{search_words}
    \  Input Text  ${search_field_selector}  ${word}
    \  Click Button  ${search_button_selector}
    \  Element Text Should Be  ${search_results_number_selector}  1

    Input Text  ${search_field_selector}  Search with no results
    Click Button  ${search_button_selector}
    Element Text Should Be  ${search_results_number_selector}  0
