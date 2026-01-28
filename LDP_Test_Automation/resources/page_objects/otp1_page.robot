*** Settings ***
Documentation    Page Object for OTP1 Page
Resource         page_base.robot
Resource         otp_common.robot

*** Keywords ***
Navigate To OTP1 Page
    [Documentation]    Navigate to OTP1 page
    Go To    ${BASE_URL}${OTP1_PAGE}
    Wait For Page To Contain    ใส่รหัสยืนยัน OTP

Enter OTP
    [Documentation]    Enter 6-digit OTP
    [Arguments]    ${otp}
    Enter OTP Digits    ${otp}    ${OTP1_INPUT_1}    ${OTP1_INPUT_2}    ${OTP1_INPUT_3}    ${OTP1_INPUT_4}    ${OTP1_INPUT_5}    ${OTP1_INPUT_6}

Verify OTP Auto Submit
    [Documentation]    Verify OTP auto-submits when 6 digits entered
    Wait Until Location Contains    select_credit_card.html    timeout=5s

Click Resend OTP
    [Documentation]    Click resend OTP link
    Click Resend OTP Link    ${OTP1_RESEND_LINK}

Verify Reference Code Changed
    [Documentation]    Verify reference code is updated after resend
    otp_common.Verify Reference Code Changed    ${OTP1_REFERENCE_CODE}    ${OTP1_RESEND_LINK}

Verify OTP Error Message
    [Documentation]    Verify OTP error message
    [Arguments]    ${expected_message}
    Verify OTP Error    ${OTP1_ERROR}    ${expected_message}

Verify Navigated To Select Card
    [Documentation]    Verify navigation to select card page
    Verify Navigation To Page    select_credit_card.html    เลือกบัตรที่ต้องการตรวจสอบ

Verify Phone Display
    [Documentation]    Verify phone number is displayed (masked)
    [Arguments]    ${expected_phone}
    Element Should Contain    ${OTP1_PHONE_DISPLAY}    ${expected_phone}
