*** Settings ***
Documentation    Page Object for Authentication Page
Resource         page_base.robot

*** Keywords ***
Navigate To Authentication Page
    [Documentation]    Navigate to authentication page
    Go To    ${BASE_URL}${AUTH_PAGE}
    Wait For Page To Contain    ตรวจสอบรายละเอียดโครงการ
    Execute JavaScript    localStorage.removeItem('phoneLockout');
    Execute JavaScript    if (typeof attemptCount !== 'undefined') { attemptCount = 0; }
    Execute JavaScript    if (typeof lockoutTime !== 'undefined') { lockoutTime = null; }

Enter ID Card
    [Documentation]    Enter ID card number (format: 1-2345-67890-12-3)
    [Arguments]    ${id_card}
    Wait Until Element Is Visible    ${AUTH_ID_CARD_INPUT}    timeout=10s
    Clear Element Text    ${AUTH_ID_CARD_INPUT}
    # Remove all dashes and format to expected pattern
    ${id_card_clean}=    Evaluate    __import__('re').sub('-', '', '${id_card}')
    Execute JavaScript    var v = '${id_card_clean}'; if (v.length === 13) { document.getElementById('idCard').value = v.substring(0,1) + '-' + v.substring(1,5) + '-' + v.substring(5,10) + '-' + v.substring(10,12) + '-' + v.substring(12,13); } else { document.getElementById('idCard').value = v; } document.getElementById('idCard').dispatchEvent(new Event('input', {bubbles: true}));

Enter Phone Number
    [Documentation]    Enter phone number (format: 082-999-9999)
    [Arguments]    ${phone}
    Wait Until Element Is Visible    ${AUTH_PHONE_INPUT}    timeout=10s
    Clear Element Text    ${AUTH_PHONE_INPUT}
    # Remove all dashes and format to expected pattern
    ${phone_clean}=    Evaluate    __import__('re').sub('-', '', '${phone}')
    Execute JavaScript    var v = '${phone_clean}'; if (v.length === 10) { document.getElementById('phoneNumber').value = v.substring(0,3) + '-' + v.substring(3,6) + '-' + v.substring(6,10); } else { document.getElementById('phoneNumber').value = v; } document.getElementById('phoneNumber').dispatchEvent(new Event('input', {bubbles: true}));

Fill Authentication Form
    [Documentation]    Fill authentication form with ID card and phone
    [Arguments]    ${id_card}    ${phone}
    Enter ID Card    ${id_card}
    Enter Phone Number    ${phone}
    # Trigger blur to validate and enable button
    Execute JavaScript    document.getElementById('idCard').dispatchEvent(new Event('blur', {bubbles: true}));
    Execute JavaScript    document.getElementById('phoneNumber').dispatchEvent(new Event('blur', {bubbles: true}));
    # Wait for button to become enabled
    Wait Until Element Is Enabled    ${AUTH_CONTINUE_BUTTON}    timeout=10s

Click Auth Continue Button
    [Documentation]    Click continue button on authentication page (expects valid data, will fail if errors shown)
    Wait Until Element Is Visible    ${AUTH_CONTINUE_BUTTON}    timeout=10s
    Wait Until Element Is Enabled    ${AUTH_CONTINUE_BUTTON}    timeout=10s
    # Trigger blur events to run validation
    Execute JavaScript    document.getElementById('idCard').dispatchEvent(new Event('blur', {bubbles: true}));
    Execute JavaScript    document.getElementById('phoneNumber').dispatchEvent(new Event('blur', {bubbles: true}));
    Wait Until Element Is Visible    ${AUTH_CONTINUE_BUTTON}    timeout=5s
    # Verify no errors are shown (for valid data test)
    ${id_card_error}=    Execute JavaScript    return document.getElementById('idCardError').style.display;
    ${phone_error}=    Execute JavaScript    return document.getElementById('phoneError').style.display;
    Should Be Equal    ${id_card_error}    none    ID Card should not have error
    Should Be Equal    ${phone_error}    none    Phone should not have error
    # Click the button
    Execute JavaScript    document.getElementById('btnContinue').disabled = false;
    Execute JavaScript    document.getElementById('btnContinue').click();
    Wait Until Location Does Not Contain    authentication.html    timeout=10s

Click Auth Continue Button Expecting Error
    [Documentation]    Click continue button expecting validation error (for error test cases)
    Wait Until Element Is Visible    ${AUTH_CONTINUE_BUTTON}    timeout=10s
    # Trigger blur events to run validation
    Execute JavaScript    document.getElementById('idCard').dispatchEvent(new Event('blur', {bubbles: true}));
    Execute JavaScript    document.getElementById('phoneNumber').dispatchEvent(new Event('blur', {bubbles: true}));
    # Try to click - validation should prevent navigation
    Execute JavaScript    document.getElementById('btnContinue').click();
    # Wait for any error to be shown (ID card or phone)
    Wait Until Page Contains Element    xpath=//*[contains(@id, 'Error') and @style='display: block;' or contains(@id, 'Error') and not(contains(@style, 'display: none'))]    timeout=5s

Verify ID Card Error Message
    [Documentation]    Verify ID card error message is displayed
    [Arguments]    ${expected_message}
    Wait Until Element Is Visible    ${AUTH_ID_CARD_ERROR}
    Element Should Contain    ${AUTH_ID_CARD_ERROR}    ${expected_message}

Verify Phone Error Message
    [Documentation]    Verify phone error message is displayed
    [Arguments]    ${expected_message}
    Wait Until Element Is Visible    ${AUTH_PHONE_ERROR}
    Element Should Contain    ${AUTH_PHONE_ERROR}    ${expected_message}

Verify Continue Button Disabled
    [Documentation]    Verify continue button is disabled
    Element Should Be Disabled    ${AUTH_CONTINUE_BUTTON}

Verify Continue Button Enabled
    [Documentation]    Verify continue button is enabled
    Element Should Be Enabled    ${AUTH_CONTINUE_BUTTON}

Verify Navigated To OTP1
    [Documentation]    Verify navigation to OTP1 page
    Verify Navigation To Page    otp1.html    ใส่รหัสยืนยัน OTP

Verify Navigated To Account Locked
    [Documentation]    Verify navigation to account locked page
    Verify Navigation To Page    account_locked.html    ระบบถูกล็อก
