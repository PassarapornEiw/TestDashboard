*** Settings ***
Documentation    Regression Test Suite - Covers both program types
Resource         ../../resources/keywords/common_keywords.robot
Resource         ../../resources/keywords/authentication_keywords.robot
Resource         ../../resources/keywords/otp_keywords.robot
Resource         ../../resources/keywords/program_keywords.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
Regression: Debt Re - Complete Flow
    [Documentation]    Regression test for complete Debt Re flow
    [Tags]    regression    debt_re
    ${test_cases}=    Get All Executable Test Cases

    FOR    ${test_case}    IN    @{test_cases}
        ${has_program_type}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${test_case}    Program_Type
        Continue For Loop If    not ${has_program_type}
        ${program_type}=    Get From Dictionary    ${test_case}    Program_Type
        Continue For Loop If    'debt re' not in '${program_type}'.lower()
        Run Keyword If    '${test_case}[Execute]' == 'Yes'    Execute Test Case    ${test_case}
    END

Regression: Rewrite Settlement - Complete Flow
    [Documentation]    Regression test for complete Rewrite Settlement flow
    [Tags]    regression    rewrite_settlement
    ${test_cases}=    Get All Executable Test Cases

    FOR    ${test_case}    IN    @{test_cases}
        ${has_program_type}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${test_case}    Program_Type
        Continue For Loop If    not ${has_program_type}
        ${program_type}=    Get From Dictionary    ${test_case}    Program_Type
        Continue For Loop If    'rewrite settlement' not in '${program_type}'.lower()
        Run Keyword If    '${test_case}[Execute]' == 'Yes'    Execute Test Case    ${test_case}
    END

*** Keywords ***
Execute Test Case
    [Documentation]    Execute individual test case
    [Arguments]    ${test_case}
    Log    Executing: ${test_case}[TestCaseNo]
