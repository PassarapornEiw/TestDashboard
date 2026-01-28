*** Settings ***
Documentation    Test Suite for Program Details - Rewrite Settlement
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/keywords/program_keywords.robot
Resource         ../../../resources/page_objects/program_details_page.robot
Resource         ../../../resources/page_objects/select_card_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_DETAIL_002: Rewrite Settlement - Verify Title And Conditions
    [Documentation]    Test rewrite settlement program details (title correct, has conditions)
    [Tags]    program_details    rewrite_settlement
    ${test_data}=    Get Test Case Data By ID    TC_DETAIL_002
    Navigate To Program Details Page    ${PROGRAM_TYPE_REWRITE_SETTLEMENT}
    Verify Rewrite Settlement Details
    Verify Program Title    โครงการปรับปรุงโครงสร้างหนี้แบบมีส่วนลด
    Verify Payment Conditions Visible
    Verify Contact Info Visible
    Update Test Result    TC_DETAIL_002    Pass

TC_DETAIL_004: Rewrite Settlement - Set New Payment Button
    [Documentation]    Test "กำหนดยอดผ่อนชำระใหม่" button navigation
    [Tags]    program_details    rewrite_settlement
    Navigate To Program Details Page    ${PROGRAM_TYPE_REWRITE_SETTLEMENT}
    Click Set New Payment Button
    program_details_page.Verify Navigated To Set Payment
    select_card_page.Verify Program Type In URL    ${PROGRAM_TYPE_REWRITE_SETTLEMENT}
