*** Settings ***
Documentation    Integration Test - Full Flow for Debt Re
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/keywords/authentication_keywords.robot
Resource         ../../../resources/keywords/otp_keywords.robot
Resource         ../../../resources/keywords/program_keywords.robot
Resource         ../../../resources/page_objects/select_card_page.robot
Resource         ../../../resources/page_objects/offering_program_page.robot
Resource         ../../../resources/page_objects/program_details_page.robot
Resource         ../../../resources/page_objects/condition_page.robot
Resource         ../../../resources/page_objects/risk_questionnaire_page.robot
Resource         ../../../resources/page_objects/e_contract_page.robot
Resource         ../../../resources/page_objects/success_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_INT_001: Full Flow - Debt Re - Interested Path
    [Documentation]    Complete registration flow for Debt Re program using "Interested" path
    [Tags]    integration    debt_re    full_flow
    ${test_data}=    Get Test Case Data By ID    TC_INT_001
    ${id_card}=    Get From Dictionary    ${test_data}    ID_Card    default=1-2345-67890-12-3
    ${phone}=    Get From Dictionary    ${test_data}    Phone_Number    default=082-999-9999
    ${card_selection}=    Get From Dictionary    ${test_data}    Card_Selection    default=card1
    ${program_type}=    Get From Dictionary    ${test_data}    Program_Type    default=debt re
    ${user_choice}=    Get From Dictionary    ${test_data}    User_Choice    default=interested
    ${reason}=    Get From Dictionary    ${test_data}    Reason    default=other

    # Authentication
    Navigate To Page    authentication.html
    Complete Authentication    ${id_card}    ${phone}

    # OTP1 - Get OTP from SMS Gateway
    ${otp1}=    Get OTP From SMS Gateway    ${phone}
    Complete OTP1    ${otp1}

    # Select Card
    Navigate To Page    select_credit_card.html?type=${program_type}
    Select Card    ${card_selection}
    Click Card Continue Button

    # Offering Program
    Navigate To Offering Program Page    ${program_type}
    Select Program    debt-restructuring
    Click Program Continue Button

    # Program Details
    Navigate To Program Details Page    ${program_type}
    Verify Debt Re Details
    Run Keyword If    '${user_choice}' == 'interested'    Click Interested Button

    # Condition
    Navigate To Condition Page    ${program_type}
    Accept Condition
    Click Condition Continue Button

    # Registration Steps
    Navigate To Page    registration_steps_info.html?type=${program_type}
    Wait For Element And Click    ${CONTINUE_BUTTON}

    # Risk Questionnaire
    Navigate To Risk Questionnaire Page
    Select Occupation    private_employee
    Fill Company Name    บริษัท ABC
    Fill Position    พนักงาน
    Fill Work Years    9
    Fill Work Months    6
    Fill Monthly Income    80000
    Fill Work Phone    023456789
    Fill Extension    123
    Fill Mobile Phone    0898765432
    Fill Email    example@email.com
    Select Reason    ${reason}
    Click Risk Continue Button
    Verify Review Page Visible
    risk_questionnaire_page.Click Confirm Button

    # E-Contract
    Navigate To E-Contract Page
    Accept Contract
    Click Accept Button

    # OTP Confirmation - Get OTP from SMS Gateway
    ${otp2}=    Get OTP From SMS Gateway    ${phone}
    Complete OTP Confirmation    ${otp2}

    # Success
    success_page.Navigate To Success Page
    Page Should Contain    ลงทะเบียนสำเร็จ

    Update Test Result    TC_INT_001    Pass
