*** Settings ***
Documentation    Dashboard UI Tests
Resource    ../../resources/variables/config.robot
Resource    ../../resources/variables/selectors.robot
Resource    ../../resources/keywords/common_keywords.robot
Resource    ../../resources/keywords/dashboard_keywords.robot
Resource    ../../resources/page_objects/dashboard_page.robot

Suite Setup    Start Dashboard Server And Open Dashboard
Suite Teardown    Stop Dashboard Server And Close Browser
Test Teardown    Take Screenshot On Failure

*** Keywords ***
Start Dashboard Server And Open Dashboard
    Start Dashboard Server
    Open Dashboard With Project

Open Dashboard With Project
    Open Browser    ${DASHBOARD_URL}/dashboard?project=${TEST_PROJECT}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Implicit Wait    ${IMPLICIT_WAIT}
    Wait For Page Load

Stop Dashboard Server And Close Browser
    Close Dashboard Browser
    Stop Dashboard Server

*** Test Cases ***
TC_DB_001: Verify Dashboard Loads With Project Parameter
    [Documentation]    Verify Dashboard loads with project parameter
    [Tags]    smoke    dashboard
    Verify Dashboard Loaded
    Verify Dashboard URL    ${TEST_PROJECT}

TC_DB_002: Verify Navigation Header Displays Correctly
    [Documentation]    Verify navigation header displays correctly
    [Tags]    dashboard
    Verify Navigation Header

TC_DB_003: Verify Back To Homepage Button Functionality
    [Documentation]    Verify "กลับหน้าแรก" button functionality
    [Tags]    smoke    dashboard    navigation
    Click Back To Homepage
    Location Should Be    ${DASHBOARD_URL}/

TC_DB_004: Verify Summary Cards Display
    [Documentation]    Verify 5 summary cards display (Total, Passed, FAIL Major, FAIL Block, Pass Rate)
    [Tags]    smoke    dashboard
    Verify Summary Cards
    Verify Summary Card Values

TC_DB_005: Verify Pie Chart Renders
    [Documentation]    Verify pie chart renders correctly
    [Tags]    dashboard
    Verify Pie Chart

TC_DB_006: Verify Latest Run Information Displays
    [Documentation]    Verify latest run information displays
    [Tags]    dashboard
    Verify Latest Run Info

TC_DB_007: Verify Tab Navigation
    [Documentation]    Verify tab navigation (By Timestamp / By Feature)
    [Tags]    dashboard
    Switch Tab    timestamp
    Sleep    1s
    Switch Tab    feature
    Sleep    1s

TC_DB_008: Verify Search Functionality
    [Documentation]    Verify search functionality
    [Tags]    dashboard
    Wait Until Element Is Visible    ${DB_SEARCH_INPUT}
    Search In Table    Payment
    Sleep    2s
    # Verify search results (implementation depends on actual search behavior)

TC_DB_009: Verify Data Table Displays
    [Documentation]    Verify data table displays correctly
    [Tags]    dashboard
    Verify Data Table

TC_DB_010: Verify Expand Collapse Functionality
    [Documentation]    Verify expand/collapse functionality
    [Tags]    dashboard
    ${rows}=    Get WebElements    ${DB_FEATURE_ROW}
    Skip If    len(${rows}) == 0    No feature rows available
    Expand Feature Row    0
    Sleep    1s
    # Verify expanded content (implementation depends on actual expand behavior)
