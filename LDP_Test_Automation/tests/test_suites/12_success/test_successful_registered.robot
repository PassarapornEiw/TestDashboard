*** Settings ***
Documentation    Test Suite for Success Page Module
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/page_objects/success_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_SUCCESS_001: Verify Success Message And Reference Number
    [Documentation]    Test success message and reference number display
    [Tags]    success    smoke
    Navigate To Success Page
    Verify Success Message
    Verify Reference Number

TC_SUCCESS_003: Finish Button Navigation
    [Documentation]    Test finish button navigation
    [Tags]    success
    Navigate To Success Page
    Click Finish Button
    Verify Navigated To Authentication
