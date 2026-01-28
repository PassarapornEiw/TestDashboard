*** Settings ***
Documentation    Test Suite for E-Contract Module
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/page_objects/e_contract_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_ECON_001: Accept Contract
    [Documentation]    Test accepting contract
    [Tags]    e_contract    smoke
    ${test_data}=    Get Test Case Data By ID    TC_ECON_001
    Navigate To E-Contract Page
    Verify Accept Button Disabled
    Accept Contract
    Verify Accept Button Enabled
    Click Accept Button
    Verify Navigated To OTP Confirmation
    Update Test Result    TC_ECON_001    Pass

TC_ECON_002: Reject Contract
    [Documentation]    Test rejecting contract navigates to survey
    [Tags]    e_contract
    Navigate To E-Contract Page
    Click Cancel Button
    Handle Alert    action=ACCEPT
    Verify Navigated To Survey

TC_ECON_004: Accept Button Disabled Until Checkbox Checked
    [Documentation]    Test accept button disabled until checkbox checked
    [Tags]    e_contract
    Navigate To E-Contract Page
    Verify Accept Button Disabled
    Accept Contract
    Verify Accept Button Enabled
