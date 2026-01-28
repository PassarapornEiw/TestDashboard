*** Settings ***
Documentation    Test Suite for Condition Module
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/page_objects/condition_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_COND_001: Accept Condition
    [Documentation]    Test accepting condition and navigation
    [Tags]    condition    smoke
    Navigate To Condition Page
    Accept Condition
    Click Condition Continue Button
    Verify Navigated To Registration Steps

TC_COND_002: Back Button Navigation
    [Documentation]    Test back button navigation
    [Tags]    condition
    Navigate To Condition Page
    condition_page.Click Condition Back Button
    condition_page.Verify Navigated To Program Details
