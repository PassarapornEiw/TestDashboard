*** Settings ***
Documentation    Test Suite for Risk Questionnaire Module
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/page_objects/risk_questionnaire_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_RISK_001: Fill All Fields - Private Employee
    [Documentation]    Test filling all fields for private employee
    [Tags]    questionnaire    smoke
    ${test_data}=    Get Test Case Data By ID    TC_RISK_001
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
    Select Reason    other
    Click Risk Continue Button
    Verify Review Page Visible
    Update Test Result    TC_RISK_001    Pass

TC_RISK_002: Change Occupation Clears Fields
    [Documentation]    Test changing occupation clears all fields
    [Tags]    questionnaire
    Navigate To Risk Questionnaire Page
    Select Occupation    private_employee
    Fill Company Name    บริษัท Test
    Fill Position    Test
    Select Occupation    business_owner
    Verify All Fields Cleared

TC_RISK_005: Edit Button Returns To Form
    [Documentation]    Test edit button returns to form
    [Tags]    questionnaire
    Navigate To Risk Questionnaire Page
    Select Occupation    private_employee
    Fill Company Name    บริษัท ABC
    Fill Position    พนักงาน
    Fill Work Years    5
    Fill Work Months    0
    Fill Monthly Income    50000
    Fill Mobile Phone    0898765432
    Fill Email    test@email.com
    Select Reason    other
    Click Risk Continue Button
    Verify Review Page Visible
    Click Edit Button
    Page Should Contain Element    ${OCCUPATION_DROPDOWN}

TC_RISK_006: Confirm Button Navigates To E-Contract
    [Documentation]    Test confirm button navigation
    [Tags]    questionnaire
    Navigate To Risk Questionnaire Page
    Select Occupation    private_employee
    Fill Company Name    บริษัท ABC
    Fill Position    พนักงาน
    Fill Work Years    5
    Fill Work Months    0
    Fill Monthly Income    50000
    Fill Mobile Phone    0898765432
    Fill Email    test@email.com
    Select Reason    other
    Click Risk Continue Button
    Verify Review Page Visible
    Click Confirm Button
    Verify Navigated To E-Contract
