*** Settings ***
Resource    ../variables/config.robot
Resource    ../variables/selectors.robot
Resource    common_keywords.robot
Resource    homepage_keywords.robot
Library    Collections

*** Keywords ***
Verify Summary Cards
    [Documentation]    Verify 5 summary cards are displayed
    Wait Until Element Is Visible    ${DB_SUMMARY_GRID}
    Verify Element Is Visible    ${DB_CARD_TOTAL}
    Verify Element Is Visible    ${DB_CARD_PASSED}
    Verify Element Is Visible    ${DB_CARD_FAILED_MAJOR}
    Verify Element Is Visible    ${DB_CARD_FAILED_BLOCK}
    Verify Element Is Visible    ${DB_CARD_PASS_RATE}

Get Summary Card Value
    [Documentation]    Get value from summary card
    [Arguments]    ${card_id}
    Wait Until Element Is Visible    ${card_id}
    ${value}=    Get Text    ${card_id}
    RETURN    ${value}

Verify Summary Card Values
    [Documentation]    Verify summary card values are not zero
    ${total}=    Get Summary Card Value    ${DB_CARD_TOTAL}
    ${passed}=    Get Summary Card Value    ${DB_CARD_PASSED}
    ${failed_major}=    Get Summary Card Value    ${DB_CARD_FAILED_MAJOR}
    ${failed_block}=    Get Summary Card Value    ${DB_CARD_FAILED_BLOCK}
    ${pass_rate}=    Get Summary Card Value    ${DB_CARD_PASS_RATE}
    
    Should Not Be Equal    ${total}    0
    Should Contain    ${pass_rate}    %

Verify Pie Chart
    [Documentation]    Verify pie chart renders
    Wait Until Element Is Visible    ${DB_PIE_CHART}
    ${chart_exists}=    Execute JavaScript    return document.getElementById('pieChart') !== null;
    Should Be True    ${chart_exists}

Verify Latest Run Info
    [Documentation]    Verify latest run information displays
    Wait Until Element Is Visible    ${DB_LATEST_RUN_INFO}
    Element Should Be Visible    ${DB_LATEST_RUN_INFO}

Switch Tab
    [Documentation]    Switch between By Timestamp / By Feature
    [Arguments]    ${tab_name}    # timestamp or feature
    ${tab_selector}=    Set Variable If    '${tab_name}' == 'timestamp'    ${DB_TAB_TIMESTAMP}    ${DB_TAB_FEATURE}
    Click Element Safely    ${tab_selector}
    Sleep    1s    # Wait for tab content to load

Search In Table
    [Documentation]    Search in data table
    [Arguments]    ${search_term}
    Wait Until Element Is Visible    ${DB_SEARCH_INPUT}
    Input Text    ${DB_SEARCH_INPUT}    ${search_term}
    Sleep    1s    # Wait for search results

Verify Data Table
    [Documentation]    Verify data table displays correctly
    Wait Until Element Is Visible    ${DB_DATA_TABLE}
    Element Should Be Visible    ${DB_DATA_TABLE}

Expand Feature Row
    [Documentation]    Expand feature row in table
    [Arguments]    ${row_index}=0
    ${rows}=    Get WebElements    ${DB_FEATURE_ROW}
    ${row}=    Get From List    ${rows}    ${row_index}
    ${expand_btn}=    Find Child Element    ${row}    ${DB_EXPAND_BUTTON}
    Click Element    ${expand_btn}
    Sleep    1s

Click View Details
    [Documentation]    Click View Details button
    [Arguments]    ${row_index}=0
    ${rows}=    Get WebElements    ${DB_FEATURE_ROW}
    ${row}=    Get From List    ${rows}    ${row_index}
    ${view_btn}=    Find Child Element    ${row}    ${DB_VIEW_DETAILS_BTN}
    Click Element    ${view_btn}
    Wait Until Element Is Visible    ${MODAL}

Verify Navigation Header
    [Documentation]    Verify navigation header displays correctly
    Wait Until Element Is Visible    ${DB_HEADER}
    Verify Element Contains Text    ${DB_HEADER_TITLE}    Test Automation Dashboard
    Verify Element Is Visible    ${DB_BACK_BUTTON}

Click Back To Homepage
    [Documentation]    Click back to homepage button
    Click Element Safely    ${DB_BACK_BUTTON}
    Wait For Page Load
    Location Should Be    ${DASHBOARD_URL}/
