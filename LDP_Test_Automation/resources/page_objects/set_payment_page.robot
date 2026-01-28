*** Settings ***
Documentation    Page Object for Set New Payment Page
Resource         page_base.robot

*** Keywords ***
Navigate To Set Payment Page
    [Documentation]    Navigate to set new payment page
    [Arguments]    ${program_type}=debt re
    Go To    ${BASE_URL}${SET_PAYMENT_PAGE}?type=${program_type}
    Wait For Page To Contain    กรอกยอดผ่อนชำระเพื่อรับข้อเสนอใหม่

Enter Payment Amount
    [Documentation]    Enter payment amount
    [Arguments]    ${amount}
    Input Text    ${PAYMENT_AMOUNT_INPUT}    ${amount}

Click Calculate Button
    [Documentation]    Click calculate button
    Click Button    ${CALCULATE_BUTTON}

Verify Calculate Button Disabled
    [Documentation]    Verify calculate button is disabled
    Element Should Be Disabled    ${CALCULATE_BUTTON}

Verify Calculate Button Enabled
    [Documentation]    Verify calculate button is enabled
    Element Should Be Enabled    ${CALCULATE_BUTTON}

Verify Calculation Result Visible
    [Documentation]    Verify calculation result is displayed
    Element Should Be Visible    ${CALCULATION_RESULT}
    Element Should Contain    ${CALCULATION_RESULT}    ผลคำนวณเบื้องต้น

Verify Payment Amount Is Zero
    [Documentation]    Verify payment amount input is 0 or empty
    ${value}=    Get Value    ${PAYMENT_AMOUNT_INPUT}
    Run Keyword If    '${value}' != '0' and '${value}' != ''    Fail    Payment amount should be 0 or empty, but was '${value}'

Click Payment Continue Button
    [Documentation]    Click continue button
    Click Continue Button    ${PAYMENT_CONTINUE_BUTTON}

Verify Navigated To Condition
    [Documentation]    Verify navigation to condition page
    Verify Navigation To Page    condition.html    ตรวจสอบเงื่อนไข

Verify Calculation Results
    [Documentation]    Verify calculation results
    [Arguments]    ${expected_interest}    ${expected_installments}    ${expected_monthly}
    Element Should Contain    ${CALC_INTEREST_RATE}    ${expected_interest}
    Element Should Contain    ${CALC_INSTALLMENTS}    ${expected_installments}
    Element Should Contain    ${CALC_MONTHLY_PAYMENT}    ${expected_monthly}
