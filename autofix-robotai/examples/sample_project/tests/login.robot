*** Settings ***
Library    AppiumLibrary
Resource   ../resources/keywords.resource

*** Test Cases ***
Login To System
    [Documentation]    Test a simple login flow in Android IVI.
    Open Android App
    Input Text Into Field    accessibility_id=username_field    testuser
    Input Text Into Field    accessibility_id=password_field    password123
    # This intentionally uses a bad locator "xpath=//bad_button" to simulate failure
    Click Button Element     xpath=//bad_btn_locator
    Wait Until Page Contains Element    id=welcome_message
    Close Application
