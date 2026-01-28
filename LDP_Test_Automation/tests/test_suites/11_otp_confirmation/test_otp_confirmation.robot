*** Settings ***
Documentation    Test Suite for OTP Confirmation Module
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/keywords/otp_keywords.robot
Resource         ../../../resources/page_objects/otp_confirmation_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_OTP2_001: Valid OTP Confirmation
    [Documentation]    Test valid OTP confirmation from SMS Gateway (auto-submit when 6 digits entered)
    [Tags]    otp2    smoke
    Navigate To OTP Confirmation Page
    # Get OTP from SMS Gateway
    ${otp}=    Get OTP From SMS Gateway    082-999-9999
    otp_confirmation_page.Enter OTP    ${otp}
    # Note: Page auto-submits when 6 digits entered, no need to click confirm
    Verify Navigated To Success

TC_OTP2_002: Wrong OTP - 3 Attempts
    [Documentation]    Test wrong OTP with 3 attempts (auto-submit)
    [Tags]    otp2    error
    Navigate To OTP Confirmation Page
    FOR    ${i}    IN RANGE    3
        # Clear previous OTP
        Execute JavaScript    document.querySelectorAll('.otp-input').forEach(input => input.value = '');
        otp_confirmation_page.Enter OTP    000000
        # Auto-submit will show error for wrong OTP
        Wait Until Element Is Visible    ${OTP2_ERROR}    timeout=5s
    END
    Verify Confirm Button Disabled

TC_OTP2_004: Resend OTP
    [Documentation]    Test resend OTP functionality
    [Tags]    otp2
    Navigate To OTP Confirmation Page
    ${initial_code}=    Get Text    ${OTP2_REFERENCE_CODE}
    otp_confirmation_page.Click Resend OTP
    Wait Until Element Is Visible    ${OTP2_REFERENCE_CODE}    timeout=3s
    ${new_code}=    Get Text    ${OTP2_REFERENCE_CODE}
    Should Not Be Equal    ${initial_code}    ${new_code}
