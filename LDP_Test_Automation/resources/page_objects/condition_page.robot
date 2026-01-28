*** Settings ***
Documentation    Page Object for Condition Page
Resource         page_base.robot

*** Keywords ***
Navigate To Condition Page
    [Documentation]    Navigate to condition page
    [Arguments]    ${program_type}=debt re
    Go To    ${BASE_URL}${CONDITION_PAGE}?type=${program_type}
    Wait For Page To Contain    ตรวจสอบเงื่อนไข

Accept Condition
    [Documentation]    Check accept condition checkbox
    Select Checkbox    ${ACCEPT_CONDITION_CHECKBOX}

Click Condition Continue Button
    [Documentation]    Click continue button
    Click Continue Button    ${CONDITION_CONTINUE_BUTTON}

Verify Navigated To Registration Steps
    [Documentation]    Verify navigation to registration steps page
    Wait Until Location Contains    registration_steps_info.html

Click Condition Back Button
    [Documentation]    Click back button
    page_base.Click Back Button    ${BACK_BUTTON}

Verify Navigated To Program Details
    [Documentation]    Verify navigation back to program details
    Wait Until Location Contains    program_details.html

Verify Navigated To Set Payment
    [Documentation]    Verify navigation back to set payment page
    Wait Until Location Contains    set_new_payment.html

Verify Condition Amounts
    [Documentation]    Verify condition amounts are displayed correctly
    [Arguments]    ${before}    ${discount}    ${after}
    Element Should Contain    ${BEFORE_CONDITION}    ${before}
    Element Should Contain    ${DISCOUNT}    ${discount}
    Element Should Contain    ${AFTER_CONDITION}    ${after}
