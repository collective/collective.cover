*** Settings ***

Resource  cover.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${folder_selector}  .contenttype-folder
${input_search}  contentchooser-search

*** Test cases ***

Test content tree tab
    Enable autologin as  Site Administrator
    Go to  ${PLONE_URL}

    Create Cover  Title  Description  Empty layout

    # For this particular test, we need some text in contents
    Go To  ${PLONE_URL}/my-document
    Click Link  link=Edit
    Input Text  id=text  A crise do apagão foi uma crise nacional ocorrida no Brasil, que afetou o fornecimento e distribuição de energia elétrica. 
    Click Button  Save
    Page Should Contain  Changes saved.

    Go To  ${PLONE_URL}/my-news-item
    Click Link  link=Edit
    Wait For Condition  return tinyMCE.activeEditor != null
    Execute Javascript  tinyMCE.activeEditor.setContent('É importante notar também que no português de Portugal, apagão é uma palavra que pode se referir a qualquer tipo de blecaute');
    Click Button  Save
    Page Should Contain  Changes saved.

    Click Link  link=Title
    Click Link  link=Compose
    Click Element  css=div#contentchooser-content-show-button

    Page Should Contain Element  css=${folder_selector}

    # Clear results before typing and wait they are loaded via AJAX
    Execute Javascript  $('#recent ul').empty();
    Input text  name=${input_search}  folder
    Wait Until Page Contains Element  css=#recent ul li a
    Xpath Should Match X Times  //div[contains(@id, 'recent')]//ul[contains(@class, 'item-list')]//li  1

    # Clear results before typing and wait they are loaded via AJAX
    Execute Javascript  $('#recent ul').empty();
    Input text  name=${input_search}  apagao
    Wait Until Page Contains Element  css=#recent ul li a
    Xpath Should Match X Times  //div[contains(@id, 'recent')]//ul[contains(@class, 'item-list')]//li  2

    # Clear results before typing and wait they are loaded via AJAX
    Execute Javascript  $('#recent ul').empty();
    Input text  name=${input_search}  apagão
    Wait Until Page Contains Element  css=#recent ul li a
    Xpath Should Match X Times  //div[contains(@id, 'recent')]//ul[contains(@class, 'item-list')]//li  2

    Go To  ${PLONE_URL}/my-document
    Click Link  link=Edit
    # For some reason, once edited, My document loads tinyMCE
    Wait For Condition  return tinyMCE.activeEditor != null
    Execute Javascript  tinyMCE.activeEditor.setContent('')
    Click Button  Save

    Go To  ${PLONE_URL}/my-news-item
    Click Link  link=Edit
    Wait For Condition  return tinyMCE.activeEditor != null
    Execute Javascript  tinyMCE.activeEditor.setContent('')
    Click Button  Save
