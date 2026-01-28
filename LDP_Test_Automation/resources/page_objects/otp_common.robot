*** Settings ***
Documentation    Common OTP keywords shared between OTP1 and OTP Confirmation pages
Resource         page_base.robot

*** Keywords ***
Enter OTP Digits
    [Documentation]    Enter 6-digit OTP using specified locator prefix
    [Arguments]    ${otp}    ${input1}    ${input2}    ${input3}    ${input4}    ${input5}    ${input6}
    ${otp_digits}=    Evaluate    list('${otp}')
    Input Text    ${input1}    ${otp_digits[0]}
    Input Text    ${input2}    ${otp_digits[1]}
    Input Text    ${input3}    ${otp_digits[2]}
    Input Text    ${input4}    ${otp_digits[3]}
    Input Text    ${input5}    ${otp_digits[4]}
    Input Text    ${input6}    ${otp_digits[5]}

Verify OTP Error
    [Documentation]    Verify OTP error message is displayed
    [Arguments]    ${error_locator}    ${expected_message}
    Wait Until Element Is Visible    ${error_locator}    timeout=5s
    Element Should Contain    ${error_locator}    ${expected_message}

Click Resend OTP Link
    [Documentation]    Click resend OTP link
    [Arguments]    ${resend_locator}
    Wait Until Element Is Visible    ${resend_locator}    timeout=10s
    Click Link    ${resend_locator}

Verify Reference Code Changed
    [Documentation]    Verify reference code changes after resend
    [Arguments]    ${ref_code_locator}    ${resend_locator}
    ${initial_code}=    Get Text    ${ref_code_locator}
    Click Resend OTP Link    ${resend_locator}
    # Wait for reference code element to update
    Wait Until Element Is Visible    ${ref_code_locator}    timeout=10s
    FOR    ${i}    IN RANGE    10
        ${new_code}=    Get Text    ${ref_code_locator}
        Exit For Loop If    '${new_code}' != '${initial_code}'
        Sleep    0.5s
    END
    Should Not Be Equal    ${initial_code}    ${new_code}
