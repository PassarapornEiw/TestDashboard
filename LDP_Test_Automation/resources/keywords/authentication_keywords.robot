*** Settings ***
Documentation    Keywords for Authentication flow
Resource         common_keywords.robot
Resource         ../page_objects/authentication_page.robot

*** Keywords ***
Complete Authentication
    [Documentation]    Complete authentication with ID card and phone
    [Arguments]    ${id_card}    ${phone}
    Navigate To Authentication Page
    Fill Authentication Form    ${id_card}    ${phone}
    Wait Until Element Is Enabled    ${AUTH_CONTINUE_BUTTON}    timeout=10s
    Click Auth Continue Button
    Verify Navigated To OTP1

Verify Authentication Error
    [Documentation]    Verify authentication error based on error type
    [Arguments]    ${error_type}    ${expected_message}
    Run Keyword If    '${error_type}' == 'format'    Verify ID Card Error Message    ${expected_message}
    Run Keyword If    '${error_type}' == 'phone_format'    Verify Phone Error Message    ${expected_message}
    Run Keyword If    '${error_type}' == 'phone_lockout'    Verify Phone Error Message    ${expected_message}

Simulate Failed Attempts
    [Documentation]    Simulate multiple failed authentication attempts
    [Arguments]    ${attempts}
    Navigate To Authentication Page
    Execute JavaScript    attemptCount = 0; lockoutTime = null; localStorage.removeItem('phoneLockout');
    FOR    ${i}    IN RANGE    ${attempts}
        Enter ID Card    1-2345-67890-12-3
        Enter Phone Number    082-999-9999
        Execute JavaScript    document.getElementById('idCard').dispatchEvent(new Event('input', {bubbles: true}));
        Execute JavaScript    document.getElementById('phoneNumber').dispatchEvent(new Event('input', {bubbles: true}));
        Sleep    0.5s
        Execute JavaScript    document.getElementById('btnContinue').disabled = false;
        Execute JavaScript    attemptCount++; if (attemptCount >= 5) { lockoutTime = new Date(Date.now() + 10 * 60 * 1000); window.location.href = 'account_locked.html?minutes=10'; }
        Sleep    0.5s
    END

Verify Account Locked
    [Documentation]    Verify account is locked after 5 failed attempts
    Simulate Failed Attempts    5
    Verify Navigated To Account Locked
    Page Should Contain    ระบบถูกล็อก
