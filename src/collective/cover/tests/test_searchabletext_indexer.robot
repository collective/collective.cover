*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${richtext_tile_location}  'collective.cover.richtext'
${basic_tile_location}  'collective.cover.basic'
${title}  Törkylempijävongahdus
${description}  Albert osti fagotin ja töräytti puhkuvan melodian.
${basic_text}  Arnold
${text}  Fahrenheit ja Celsius yrjösivät Åsan backgammon-peliin, Volkswagenissa, daiquirin ja ZX81:n yhteisvaikutuksesta.
${richtext_edit_link_selector}  css=a.edit-tile-link[rel='#pb_2']
${basic_edit_link_selector}  css=a.edit-tile-link[rel='#pb_3']
${title_field_id}  collective-cover-basic-title
${search_field_selector}  id=searchGadget
${search_button_selector}  css=.searchButton
@{search_words}  torkylempijavongahdus  Törkylempijävongahdus  töräytti  Fahrenheit  Åsan Arnold
${search_results_number_selector}  xpath=//strong[@id='search-results-number']

*** Test cases ***

Test RichTextTile is Searchable
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Cover  ${title}  ${description}
    Open Layout Tab
    Add Tile  ${richtext_tile_location}
    Add Tile  ${basic_tile_location}
    Save Cover Layout

    # Add the text to the richtext tile
    Compose Cover
    Click Link  ${richtext_edit_link_selector}
    Wait For Condition  return typeof tinyMCE != "undefined" && tinyMCE.activeEditor != null
    Execute Javascript  tinyMCE.activeEditor.setContent("${text}");
    Click Button  Save
    Wait Until Page Contains  ${text}

    # Add the text to the basic tile
    Compose Cover
    Click Link  ${basic_edit_link_selector}
    Wait until page contains element  id=${title_field_id}
    Input Text  id=${title_field_id}  ${basic_text}
    Click Button  Save
    Wait Until Page Contains  ${basic_text}

    # Make a number of searches to verify the index
    : FOR  ${word}  IN  @{search_words}
    \  Input Text  ${search_field_selector}  ${word}
    \  Click Button  ${search_button_selector}
    \  Element Text Should Be  ${search_results_number_selector}  1

    Input Text  ${search_field_selector}  Search with no results
    Click Button  ${search_button_selector}
    Element Text Should Be  ${search_results_number_selector}  0
