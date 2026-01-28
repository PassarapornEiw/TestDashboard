*** Settings ***
Documentation    Test Suite for OTP1 Module
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/keywords/otp_keywords.robot
Resource         ../../../resources/page_objects/otp1_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_OTP1_001: Valid OTP
    [Documentation]    Test valid OTP from SMS Gateway
    [Tags]    otp1    smoke
    ${test_data}=    Get Test Case Data By ID    TC_OTP1_001
    ${phone}=    Get From Dictionary    ${test_data}    Phone_Number    default=082-999-9999
    Navigate To OTP1 Page
    # Get OTP from SMS Gateway
    ${otp}=    Get OTP From SMS Gateway    ${phone}
    otp1_page.Enter OTP    ${otp}
    Verify Navigated To Select Card
    Update Test Result    TC_OTP1_001    Pass

TC_OTP1_002: Wrong OTP
    [Documentation]    Test wrong OTP error handling
    [Tags]    otp1    error
    ${test_data}=    Get Test Case Data By ID    TC_OTP1_002
    Navigate To OTP1 Page
    otp1_page.Enter OTP    000000
    Wait Until Element Is Visible    ${OTP1_ERROR}    timeout=3s
    otp1_page.Verify OTP Error Message    ไม่ถูกต้อง
    Update Test Result    TC_OTP1_002    Pass

TC_OTP1_004: Auto Submit When 6 Digits Entered
    [Documentation]    Test OTP auto-submit when 6 digits entered via SMS Gateway
    [Tags]    otp1
    Navigate To OTP1 Page
    # Get OTP from SMS Gateway using default phone
    ${otp}=    Get OTP From SMS Gateway    082-999-9999
    otp1_page.Enter OTP    ${otp}
    Verify OTP Auto Submit

TC_OTP1_005: Resend OTP
    [Documentation]    Test resend OTP functionality
    [Tags]    otp1
    Navigate To OTP1 Page
    Resend OTP And Verify
