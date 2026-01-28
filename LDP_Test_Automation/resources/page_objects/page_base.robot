*** Settings ***
Documentation    Base resource for all page objects - contains common libraries and variables
Library          SeleniumLibrary
Library          Collections
Resource         ../variables/locators.robot
Resource         ../variables/common_variables.robot

*** Keywords ***
Click Continue Button
    [Documentation]    Click continue button with specified locator
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    timeout=10s
    Wait Until Element Is Enabled    ${locator}    timeout=10s
    Click Button    ${locator}

Click Back Button
    [Documentation]    Click back button
    [Arguments]    ${locator}=${BACK_BUTTON}
    Wait Until Element Is Visible    ${locator}    timeout=10s
    Click Element    ${locator}

Wait For Page To Contain
    [Documentation]    Wait for page to contain specific text
    [Arguments]    ${text}    ${timeout}=10s
    Wait Until Page Contains    ${text}    timeout=${timeout}

Verify Navigation To Page
    [Documentation]    Verify navigation to page by URL and content
    [Arguments]    ${url_contains}    ${page_content}    ${timeout}=30s
    Wait Until Location Contains    ${url_contains}    timeout=${timeout}
    Page Should Contain    ${page_content}
