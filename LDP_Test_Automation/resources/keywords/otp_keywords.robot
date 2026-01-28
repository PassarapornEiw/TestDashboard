*** Settings ***
Documentation    Keywords for OTP flows
Resource         common_keywords.robot
Resource         ../page_objects/otp1_page.robot
Resource         ../page_objects/otp_confirmation_page.robot
Library          ../libraries/otp_provider.py    WITH NAME    OTPProvider
Library          Collections
Library          DateTime
Library          OperatingSystem

*** Variables ***
${SMS_OTP_EVIDENCE_DIR}    results${/}sms_otp_evidence

*** Keywords ***
Get OTP From SMS Gateway
    [Documentation]    Trigger and retrieve OTP from SMS_OTP Gateway using Robot Framework
    ...    Opens new tab, logs in, sends mock OTP, takes screenshots, and retrieves the code
    ...    Filters by today's date only
    [Arguments]    ${phone_number}
    Log    ========== SMS_OTP Gateway ==========    console=True
    Log    Phone: ${phone_number}    console=True
    
    # Format phone number
    ${formatted_phone}=    Format Phone For SMS Gateway    ${phone_number}
    Log    Formatted Phone: ${formatted_phone}    console=True
    
    # Store current window handle
    ${main_window}=    Get Window Handles
    ${main_window}=    Get From List    ${main_window}    0
    
    # Open new tab for SMS_OTP
    Execute JavaScript    window.open('about:blank', '_blank');
    ${all_windows}=    Get Window Handles
    ${sms_window}=    Get From List    ${all_windows}    -1
    Switch Window    ${sms_window}
    
    # Login to SMS Gateway
    Login To SMS Gateway
    
    # Send Mock OTP
    Send Mock OTP In Gateway    ${formatted_phone}
    
    # Filter by today and get OTP
    ${otp}=    Get OTP Value From Table    ${formatted_phone}
    
    # Close SMS_OTP tab and switch back
    Close Window
    Switch Window    ${main_window}
    
    Log    OTP Code Retrieved: ${otp}    console=True
    Log    ========================================    console=True
    RETURN    ${otp}

 Login To SMS Gateway
    [Documentation]    Login to SMS_OTP Gateway and take screenshot
    ${sms_otp_url}=    Get SMS OTP Config    url
    ${username}=    Get SMS OTP Config    username
    ${password}=    Get SMS OTP Config    password
    
    Go To    ${sms_otp_url}/login
    Wait Until Page Contains    QA SMS Gateway    timeout=10s
    
    # Enter credentials
    Input Text    id=username    ${username}
    Input Text    id=password    ${password}
    
    # Click login button
    Click Button    xpath=//button[@type='submit']
    
    # Wait for redirect to SMS_Smart page
    Wait Until Location Contains    SMS_Smart    timeout=10s
    Wait Until Page Contains    QA SMS Gateway    timeout=10s
    
    # Take screenshot after login
    Take SMS Gateway Screenshot    01_login_success

Send Mock OTP In Gateway
    [Documentation]    Send mock OTP to phone number and take screenshot
    [Arguments]    ${phone_number}
    
    # Wait for Send Mock OTP section
    Wait Until Element Is Visible    xpath=//input[@type='tel' and contains(@placeholder, 'Phone Number')]    timeout=10s
    
    # Enter phone number
    Input Text    xpath=//input[@type='tel' and contains(@placeholder, 'Phone Number')]    ${phone_number}
    
    # Click Send Mock OTP button
    Click Button    xpath=//button[contains(., 'Send Mock OTP')]
    
    # Wait for success toast
    Wait Until Page Contains    OTP sent successfully    timeout=10s
    
    # Take screenshot after sending OTP
    Take SMS Gateway Screenshot    02_otp_sent

Get OTP Value From Table
    [Documentation]    Filter by today, get OTP from table, and take screenshot
    [Arguments]    ${phone_number}
    
    # Set date filter to today
    Set Date Filter To Today
    
    # Wait for table to load
    Wait Until Element Is Visible    xpath=//table//tbody    timeout=10s
    
    # Take screenshot of OTP table
    Take SMS Gateway Screenshot    03_otp_table
    
    # Get OTP from first row (most recent)
    ${otp}=    Get Text    xpath=//table//tbody//tr[1]//td[3]//span[contains(@class, 'font-mono')]
    
    Log    Retrieved OTP: ${otp}    console=True
    RETURN    ${otp}

Set Date Filter To Today
    [Documentation]    Set date filter to today's date
    ${today}=    Get Current Date    result_format=%d/%m/%Y
    
    # Click From date input
    Click Element    xpath=//input[@placeholder='From (DD/MM/YYYY)']
    Sleep    0.5s
    
    # Get today's day number
    ${day}=    Get Current Date    result_format=%d
    ${day}=    Evaluate    int(${day})
    
    # Click today's date in calendar
    Wait Until Element Is Visible    xpath=//button[normalize-space()='${day}']    timeout=5s
    Click Element    xpath=//button[normalize-space()='${day}']
    Sleep    0.5s
    
    # Click To date input
    Click Element    xpath=//input[@placeholder='To (DD/MM/YYYY)']
    Sleep    0.5s
    
    # Click today's date in calendar
    Wait Until Element Is Visible    xpath=//button[normalize-space()='${day}']    timeout=5s
    Click Element    xpath=//button[normalize-space()='${day}']
    Sleep    0.5s

Take SMS Gateway Screenshot
    [Documentation]    Take screenshot and save to sms_otp_evidence directory
    [Arguments]    ${screenshot_name}
    
    # Create evidence directory if not exists
    Create Directory    ${SMS_OTP_EVIDENCE_DIR}
    
    # Generate timestamp for unique filename
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${filename}=    Set Variable    sms_otp_${screenshot_name}_${timestamp}.png
    ${filepath}=    Set Variable    ${SMS_OTP_EVIDENCE_DIR}${/}${filename}
    
    # Take screenshot
    Capture Page Screenshot    ${filepath}
    
    Log    Screenshot saved: ${filepath}    console=True


Complete OTP1
    [Documentation]    Complete OTP1 verification
    [Arguments]    ${otp}=123456
    Navigate To OTP1 Page
    otp1_page.Enter OTP    ${otp}
    Verify Navigated To Select Card

Complete OTP Confirmation
    [Documentation]    Complete OTP2 confirmation (auto-submit when 6 digits entered)
    [Arguments]    ${otp}=123456
    Navigate To OTP Confirmation Page
    otp_confirmation_page.Enter OTP    ${otp}
    # Note: Page auto-submits when 6 digits entered, no need to click confirm
    Verify Navigated To Success

Verify OTP Error And Retry
    [Documentation]    Verify OTP error and retry with correct OTP
    [Arguments]    ${wrong_otp}    ${correct_otp}
    otp1_page.Enter OTP    ${wrong_otp}
    Wait Until Element Is Visible    ${OTP1_ERROR}    timeout=3s
    otp1_page.Verify OTP Error Message    ไม่ถูกต้อง
    otp1_page.Enter OTP    ${correct_otp}
    Verify Navigated To Select Card

Resend OTP And Verify
    [Documentation]    Resend OTP and verify reference code changes
    ${initial_code}=    Get Text    ${OTP1_REFERENCE_CODE}
    otp1_page.Click Resend OTP
    Wait Until Element Is Visible    ${OTP1_REFERENCE_CODE}    timeout=3s
    ${new_code}=    Get Text    ${OTP1_REFERENCE_CODE}
    Should Not Be Equal    ${initial_code}    ${new_code}
