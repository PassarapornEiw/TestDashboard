*** Settings ***
Documentation    Test Suite for Select Credit Card Module
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/page_objects/select_card_page.robot


Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_CARD_001: Select Eligible Card
    [Documentation]    Test selecting eligible card
    [Tags]    select_card    smoke
    ${test_data}=    Get Test Case Data By ID    TC_CARD_001
    Navigate To Select Card Page
    ${card_selection}=    Get From Dictionary    ${test_data}    Card_Selection    default=card1
    Select Card    ${card_selection}
    Click Card Continue Button
    Verify Navigated To Offering Program
    Update Test Result    TC_CARD_001    Pass

TC_CARD_002: Disabled Card Cannot Select
    [Documentation]    Test disabled card (registered) cannot be selected
    [Tags]    select_card
    Navigate To Select Card Page
    Verify Card Disabled    card3
    Verify Card Enabled    card1

TC_CARD_004: Verify Program Type Passed
    [Documentation]    Verify programType is passed correctly
    [Tags]    select_card
    Navigate To Page    select_credit_card.html?type=${PROGRAM_TYPE_DEBT_RE}
    Select Card    card1
    Click Card Continue Button
    Verify Program Type In URL    ${PROGRAM_TYPE_DEBT_RE}
