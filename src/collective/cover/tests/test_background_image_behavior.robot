*** Settings ***

Resource  cover.robot
Variables  utils.py
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${BACKGROUND_IMAGE_BEHAVIOR_SELECTOR}  form-widgets-collective-cover-behaviors-interfaces-IBackgroundImage-0
${BACKGROUND_IMAGE_BUTTON_SELECTOR}  form-widgets-IBackgroundImage-background_image-input
${BACKGROUND_IMAGE_STYLE}  background: url("@@images/background_image")
${COVER_BEHAVIORS_URL}  dexterity-types/collective.cover.content/@@behaviors
${IMAGE}  ${BUILDOUT_DIRECTORY}/src/collective/cover/testing/input/canoneye.jpg

*** Test cases ***

Test Background Image Behavior
    [Documentation]  Enable IBackgroundImage behavior and test the field is
    ...              present; check the code on the default view: if no image
    ...              has been set, there should be no code related with image
    ...              background; if an image is set, the the code should be
    ...              present. Disabling the IBackgroundImage behavior should
    ...              not break anything. We need to log as Manage to access
    ...              the behavior settings on the control panel.

    Enable Autologin as  Manager

    Enable Background Image Behavior
    Go to Homepage
    Create Cover  Frontpage  Test for background image behavior
    # no image added yet, no background image code should be present
    Page Should Not Contain  ${BACKGROUND_IMAGE_STYLE}

    # after adding an image, the background image code should be present
    Click Link  link=Edit
    Page Should Contain  Background image
    Page Should Contain Button  id=${BACKGROUND_IMAGE_BUTTON_SELECTOR}
    Choose File  id=${BACKGROUND_IMAGE_BUTTON_SELECTOR}  ${IMAGE}
    Click Button  Save
    Page Should Contain  Changes saved
    Page Should Contain  ${BACKGROUND_IMAGE_STYLE}

    # after disabling the behavior, no background image code is present again
    Disable Background Image Behavior
    Go to Homepage
    Click Link  Frontpage
    Page Should Not Contain  ${BACKGROUND_IMAGE_STYLE}
    Click Link  link=Edit
    Page Should Not Contain  Background image

*** Keywords ***

Go to Cover Behaviors
    Go to  ${PLONE_URL}/${COVER_BEHAVIORS_URL}

Enable Background Image Behavior
    Go to Cover Behaviors
    Page Should Contain  Background image
    Page Should Contain Checkbox  id=${BACKGROUND_IMAGE_BEHAVIOR_SELECTOR}
    Select Checkbox  id=${BACKGROUND_IMAGE_BEHAVIOR_SELECTOR}
    Click Button  Save
    Checkbox Should Be Selected  id=${BACKGROUND_IMAGE_BEHAVIOR_SELECTOR}

Disable Background Image Behavior
    Go to Cover Behaviors
    Page Should Contain  Background image
    Page Should Contain Checkbox  id=${BACKGROUND_IMAGE_BEHAVIOR_SELECTOR}
    Unselect Checkbox  id=${BACKGROUND_IMAGE_BEHAVIOR_SELECTOR}
    Click Button  Save
    Checkbox Should Not Be Selected  id=${BACKGROUND_IMAGE_BEHAVIOR_SELECTOR}
