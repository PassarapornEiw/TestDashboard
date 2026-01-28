*** Settings ***
Documentation    Test Suite for Program Details - Debt Re
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/keywords/program_keywords.robot
Resource         ../../../resources/page_objects/program_details_page.robot
Resource         ../../../resources/page_objects/select_card_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_DETAIL_001: Debt Re - Verify Title And No Conditions
    [Documentation]    Test debt re program details (title correct, no conditions)
    [Tags]    program_details    debt_re
    ${test_data}=    Get Test Case Data By ID    TC_DETAIL_001
    Navigate To Program Details Page    ${PROGRAM_TYPE_DEBT_RE}
    Verify Debt Re Details
    Verify Program Title    โครงการปรับปรุงโครงสร้างหนี้
    Verify Payment Conditions Not Visible
    Verify Contact Info Not Visible
    Update Test Result    TC_DETAIL_001    Pass

TC_DETAIL_003: Debt Re - Interested Button
    [Documentation]    Test "สนใจในข้อเสนอนี้" button navigation
    [Tags]    program_details    debt_re
    Navigate To Program Details Page    ${PROGRAM_TYPE_DEBT_RE}
    Click Interested Button
    program_details_page.Verify Navigated To Condition
    select_card_page.Verify Program Type In URL    ${PROGRAM_TYPE_DEBT_RE}
