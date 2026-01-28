*** Settings ***
Documentation    Test Suite for Set New Payment Module
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/keywords/payment_keywords.robot
Resource         ../../../resources/page_objects/set_payment_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_PAY_001: Enter Amount And Calculate
    [Documentation]    Test entering amount and calculating payment
    [Tags]    payment
    ${test_data}=    Get Test Case Data By ID    TC_PAY_001
    Navigate To Set Payment Page
    ${payment_amount}=    Get From Dictionary    ${test_data}    Payment_Amount    default=1000
    Enter Payment Amount    ${payment_amount}
    Verify Calculate Button Enabled
    Click Calculate Button
    Verify Calculation Result Visible
    Update Test Result    TC_PAY_001    Pass

TC_PAY_003: Back From Condition Resets Payment
    [Documentation]    Test back from condition resets payment to 0
    [Tags]    payment
    Test Back From Condition Resets Payment

TC_PAY_004: Calculate Button Disabled When Amount Zero
    [Documentation]    Test calculate button disabled when amount is 0
    [Tags]    payment
    Navigate To Set Payment Page
    Verify Payment Amount Is Zero
    Verify Calculate Button Disabled
