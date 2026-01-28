*** Settings ***
Documentation    Page Object for E-Contract Page
Resource         page_base.robot

*** Keywords ***
Navigate To E-Contract Page
    [Documentation]    Navigate to E-Contract page
    Go To    ${BASE_URL}${E_CONTRACT_PAGE}
    Wait For Page To Contain    สัญญาโครงการปรับปรุงโครงสร้างหนี้
    # Wait for contract elements to be ready
    Wait Until Element Is Visible    ${ACCEPT_CONTRACT_CHECKBOX}    timeout=10s
    Wait Until Element Is Visible    ${BTN_ACCEPT}    timeout=10s

Accept Contract
    [Documentation]    Check accept contract checkbox
    Wait Until Element Is Visible    ${ACCEPT_CONTRACT_CHECKBOX}    timeout=10s
    Select Checkbox    ${ACCEPT_CONTRACT_CHECKBOX}

Click Accept Button
    [Documentation]    Click accept button
    Wait Until Element Is Visible    ${BTN_ACCEPT}    timeout=10s
    Wait Until Element Is Enabled    ${BTN_ACCEPT}    timeout=10s
    Click Button    ${BTN_ACCEPT}
    # Wait for navigation to OTP confirmation
    Wait Until Location Does Not Contain    e_contract    timeout=15s

Click Cancel Button
    [Documentation]    Click cancel button
    Wait Until Element Is Visible    ${BTN_CANCEL}    timeout=10s
    Click Button    ${BTN_CANCEL}

Verify Accept Button Disabled
    [Documentation]    Verify accept button is disabled
    Element Should Be Disabled    ${BTN_ACCEPT}

Verify Accept Button Enabled
    [Documentation]    Verify accept button is enabled
    Element Should Be Enabled    ${BTN_ACCEPT}

Verify Navigated To OTP Confirmation
    [Documentation]    Verify navigation to OTP confirmation page
    Verify Navigation To Page    otp_confirmation.html    ใส่รหัสยืนยัน OTP

Verify Navigated To Survey
    [Documentation]    Verify navigation to survey page (if rejected)
    Wait Until Location Contains    survey.html    timeout=15s

Verify Contract Data
    [Documentation]    Verify contract data is displayed correctly
    [Arguments]    ${name}    ${id_card}    ${card_name}    ${card_number}
    Element Should Contain    ${CONTRACT_NAME}    ${name}
    Element Should Contain    ${CONTRACT_ID_CARD}    ${id_card}
    Element Should Contain    xpath=//span[@id='contractDebtInfo']    ${card_name}
    Element Should Contain    xpath=//span[@id='contractLoanType']    ${card_number}
