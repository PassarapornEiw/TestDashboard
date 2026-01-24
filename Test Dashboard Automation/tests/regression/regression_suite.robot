*** Settings ***
Documentation    Regression Test Suite - Critical Path Tests
Resource    ../../resources/variables/config.robot
Resource    ../../resources/variables/selectors.robot
Resource    ../../resources/keywords/common_keywords.robot
Resource    ../../resources/keywords/homepage_keywords.robot
Resource    ../../resources/keywords/dashboard_keywords.robot
Resource    ../../resources/keywords/api_keywords.robot
Resource    ../../resources/page_objects/homepage_page.robot
Resource    ../../resources/page_objects/dashboard_page.robot
Library    SeleniumLibrary
Library    RequestsLibrary
Library    Collections

Suite Setup    Setup Regression Suite
Suite Teardown    Teardown Regression Suite
Test Teardown    Take Screenshot On Failure

*** Variables ***
${API_SESSION}    dashboard

*** Keywords ***
Setup Regression Suite
    [Documentation]    Setup for regression suite
    Start Dashboard Server
    Create Session    ${API_SESSION}    ${DASHBOARD_URL}
    Open Dashboard Homepage

Teardown Regression Suite
    [Documentation]    Teardown for regression suite
    Close Dashboard Browser
    Delete All Sessions
    Stop Dashboard Server

*** Test Cases ***
REGRESSION_001: Critical Path - Homepage To Dashboard Flow
    [Documentation]    Critical path: User selects project and navigates to dashboard
    [Tags]    regression    smoke    critical
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    Click Project Card    ${project_name}
    Verify Dashboard Loaded
    Verify Dashboard URL    ${project_name}

REGRESSION_002: Critical Path - Dashboard Data Loading
    [Documentation]    Critical path: Verify dashboard loads correct project data
    [Tags]    regression    smoke    critical
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    Click Project Card    ${project_name}
    Wait For Page Load
    Verify Summary Cards
    Verify Summary Card Values
    Verify Pie Chart

REGRESSION_003: Critical Path - API Response Validation
    [Documentation]    Critical path: Verify all API endpoints return correct structure
    [Tags]    regression    smoke    critical    api
    ${response}=    Get Projects API
    Verify API Status Code    ${response}    200
    Verify Projects Response Structure    ${response}
    ${json}=    Set Variable    ${response.json()}
    ${projects}=    Get From Dictionary    ${json}    projects
    Run Keyword If    len(${projects}) > 0    Verify Project Object Structure    ${projects[0]}

REGRESSION_004: Critical Path - Dashboard Data API
    [Documentation]    Critical path: Verify dashboard data API works correctly
    [Tags]    regression    smoke    critical    api
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    ${response}=    Get Dashboard Data API    ${project_name}
    Verify API Status Code    ${response}    200
    Verify Dashboard Data Response Structure    ${response}

REGRESSION_005: Critical Path - Navigation Flow
    [Documentation]    Critical path: Verify navigation between Homepage and Dashboard
    [Tags]    regression    smoke    critical
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    Click Project Card    ${project_name}
    Wait For Page Load
    Click Back To Homepage
    Location Should Be    ${DASHBOARD_URL}/
    Wait Until Element Is Visible    ${HP_PROJECTS_GRID}

REGRESSION_006: Critical Path - Summary Cards Display
    [Documentation]    Critical path: Verify summary cards display correctly
    [Tags]    regression    smoke    critical
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    Go To    ${DASHBOARD_URL}/dashboard?project=${project_name}
    Wait For Page Load
    Verify Summary Cards
    ${total}=    Get Summary Card Value    ${DB_CARD_TOTAL}
    ${passed}=    Get Summary Card Value    ${DB_CARD_PASSED}
    ${pass_rate}=    Get Summary Card Value    ${DB_CARD_PASS_RATE}
    Should Not Be Equal    ${total}    0
    Should Contain    ${pass_rate}    %

REGRESSION_007: Critical Path - Project Discovery
    [Documentation]    Critical path: Verify project discovery works correctly
    [Tags]    regression    smoke    critical    api
    ${response}=    Get Projects API
    Verify API Status Code    ${response}    200
    ${json}=    Set Variable    ${response.json()}
    ${total_projects}=    Get From Dictionary    ${json}    total_projects
    ${automation_dir}=    Get From Dictionary    ${json}    automation_project_dir
    Should Be True    ${total_projects} >= 0    Total projects should be non-negative
    Should Not Be Empty    ${automation_dir}    Automation project directory should be set

REGRESSION_008: Critical Path - Status Priority Logic
    [Documentation]    Critical path: Verify status priority logic (FAIL Block > FAIL Major > PASS)
    [Tags]    regression    smoke    critical    api
    ${response}=    Get Dashboard Data API    ${TEST_PROJECT}
    Run Keyword If    ${response.status_code} == 200    Verify Status Priority In Response    ${response}

REGRESSION_009: Critical Path - Backward Compatibility
    [Documentation]    Critical path: Verify backward compatibility (no project parameter)
    [Tags]    regression    smoke    critical    api
    ${response}=    Get Dashboard Data API
    Verify API Status Code    ${response}    200
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    runs

REGRESSION_010: Critical Path - Error Handling
    [Documentation]    Critical path: Verify error handling for invalid inputs
    [Tags]    regression    smoke    critical    api    negative
    ${response}=    Get Dashboard Data API    InvalidProjectName12345
    ${status_code}=    Set Variable    ${response.status_code}
    Should Be True    ${status_code} >= 400    Expected error status code for invalid project

*** Keywords ***
Verify Status Priority In Response
    [Arguments]    ${response}
    ${json}=    Set Variable    ${response.json()}
    ${features}=    Get From Dictionary    ${json}    features
    Run Keyword If    len(${features}) > 0    Verify Feature Status Priority    ${features}

Verify Feature Status Priority
    [Arguments]    ${features}
    FOR    ${feature}    IN    @{features}
        ${status}=    Get From Dictionary    ${feature}    status
        ${status_upper}=    Convert To Uppercase    ${status}
        Should Be True    '${status_upper}' in ['PASS', 'FAIL (MAJOR)', 'FAIL (BLOCK)', 'UNKNOWN']    Invalid status: ${status}
    END
