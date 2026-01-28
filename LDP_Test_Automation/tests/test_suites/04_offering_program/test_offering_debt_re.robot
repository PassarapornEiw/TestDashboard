*** Settings ***
Documentation    Test Suite for Offering Program - Debt Re
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/keywords/program_keywords.robot
Resource         ../../../resources/page_objects/offering_program_page.robot
Resource         ../../../resources/page_objects/select_card_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_PROG_001: Debt Re - Show 2 Programs
    [Documentation]    Test debt re program display (2 programs, none selected)
    [Tags]    offering_program    debt_re
    ${test_data}=    Get Test Case Data By ID    TC_PROG_001
    Navigate To Offering Program Page    ${PROGRAM_TYPE_DEBT_RE}
    Verify Debt Re Display
    Verify Program Count    2
    Verify Program Not Selected    debt-restructuring
    Update Test Result    TC_PROG_001    Pass

TC_PROG_003: Select Debt Re Program
    [Documentation]    Test selecting debt re program
    [Tags]    offering_program    debt_re
    Navigate To Offering Program Page    ${PROGRAM_TYPE_DEBT_RE}
    Select Program    debt-restructuring
    Click Program Continue Button
    Verify Navigated To Program Details
    select_card_page.Verify Program Type In URL    ${PROGRAM_TYPE_DEBT_RE}
