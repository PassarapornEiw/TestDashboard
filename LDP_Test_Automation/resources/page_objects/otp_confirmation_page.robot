*** Settings ***
Documentation    Page Object for OTP Confirmation Page
Resource         page_base.robot
Resource         otp_common.robot

*** Keywords ***
Navigate To OTP Confirmation Page
    [Documentation]    Navigate to OTP confirmation page
    Go To    ${BASE_URL}${OTP_CONFIRMATION_PAGE}
    Wait For Page To Contain    ใส่รหัสยืนยัน OTP
    # Wait for OTP input fields to be ready
    Wait Until Element Is Visible    ${OTP2_INPUT_1}    timeout=10s
    Wait Until Element Is Visible    ${OTP2_CONFIRM_BUTTON}    timeout=10s

Enter OTP
    [Documentation]    Enter 6-digit OTP (note: page auto-submits when 6 digits entered)
    [Arguments]    ${otp}
    # Wait for first input to be ready
    Wait Until Element Is Visible    ${OTP2_INPUT_1}    timeout=10s
    otp_common.Enter OTP Digits    ${otp}    ${OTP2_INPUT_1}    ${OTP2_INPUT_2}    ${OTP2_INPUT_3}    ${OTP2_INPUT_4}    ${OTP2_INPUT_5}    ${OTP2_INPUT_6}
    # Wait for auto-submit to process (page will navigate away for correct OTP)
    Sleep    0.5s

Click Confirm Button
    [Documentation]    Click confirm button
    Wait Until Element Is Visible    ${OTP2_CONFIRM_BUTTON}    timeout=10s
    Wait Until Element Is Enabled    ${OTP2_CONFIRM_BUTTON}    timeout=10s
    Click Button    ${OTP2_CONFIRM_BUTTON}

Click Resend OTP
    [Documentation]    Click resend OTP link
    Click Resend OTP Link    ${OTP2_RESEND_LINK}

Verify OTP Error Message
    [Documentation]    Verify OTP error message
    [Arguments]    ${expected_message}
    Verify OTP Error    ${OTP2_ERROR}    ${expected_message}

Verify Navigated To Success
    [Documentation]    Verify navigation to success page
    Verify Navigation To Page    successful_registered.html    ลงทะเบียนสำเร็จ

Verify Confirm Button Disabled
    [Documentation]    Verify confirm button is disabled (after max attempts)
    Element Should Be Disabled    ${OTP2_CONFIRM_BUTTON}
