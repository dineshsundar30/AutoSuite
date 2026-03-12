*** Settings ***
Library    AppiumLibrary

*** Keywords ***
Open Android App
    Open Application    http://localhost:4723/wd/hub    platformName=Android    deviceName=emulator-5554    appPackage=com.example.ivi    appActivity=.MainActivity

Input Text Into Field
    [Arguments]    ${locator}    ${text}
    Wait Until Element Is Visible    ${locator}    timeout=5s
    Input Text    ${locator}    ${text}

Click Button Element
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    timeout=5s
    Click Element    ${locator}
