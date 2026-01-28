*** Settings ***
Documentation    Keywords for payment calculation
Resource         common_keywords.robot
Resource         ../page_objects/set_payment_page.robot
Resource         ../page_objects/condition_page.robot

*** Keywords ***
Calculate Payment
    [Documentation]    Enter amount and calculate payment
    [Arguments]    ${amount}
    Navigate To Set Payment Page
    Enter Payment Amount    ${amount}
    Verify Calculate Button Enabled
    Click Calculate Button
    Verify Calculation Result Visible

Verify Payment Calculation
    [Documentation]    Verify payment calculation results
    [Arguments]    ${amount}    ${expected_interest}    ${expected_installments}    ${expected_monthly}
    Calculate Payment    ${amount}
    Verify Calculation Results    ${expected_interest}    ${expected_installments}    ${expected_monthly}

Test Back From Condition Resets Payment
    [Documentation]    Test that back from condition resets payment to 0
    Navigate To Set Payment Page
    Enter Payment Amount    1000
    Click Calculate Button
    Click Payment Continue Button
    set_payment_page.Verify Navigated To Condition
    condition_page.Click Condition Back Button
    condition_page.Verify Navigated To Set Payment
    Verify Payment Amount Is Zero
