*** Settings ***
Documentation    Test Suite for Offering Program - Rewrite Settlement
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/keywords/program_keywords.robot
Resource         ../../../resources/page_objects/offering_program_page.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_PROG_002: Rewrite Settlement - Show 1 Program With Discount
    [Documentation]    Test rewrite settlement program display (1 program, selected, with discount)
    [Tags]    offering_program    rewrite_settlement
    ${test_data}=    Get Test Case Data By ID    TC_PROG_002
    Navigate To Offering Program Page    ${PROGRAM_TYPE_REWRITE_SETTLEMENT}
    Verify Rewrite Settlement Display
    Verify Program Count    1
    Verify Program Selected    debt-restructuring-discount
    Verify Program Has Discount    83,666
    Update Test Result    TC_PROG_002    Pass
