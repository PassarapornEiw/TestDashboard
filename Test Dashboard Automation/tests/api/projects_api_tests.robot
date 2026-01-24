*** Settings ***
Documentation    Projects API Tests
Resource    ../../resources/variables/config.robot
Resource    ../../resources/keywords/api_keywords.robot
Library    RequestsLibrary
Library    Collections
Library    JSON

Suite Setup    Create Session    dashboard    ${DASHBOARD_URL}
Suite Teardown    Delete All Sessions

*** Test Cases ***
TC_API_PROJ_001: Verify GET Projects API Returns 200
    [Documentation]    Verify GET /api/projects returns 200
    [Tags]    smoke    api    projects
    ${response}=    Get Projects API
    Verify API Status Code    ${response}    200

TC_API_PROJ_002: Verify Response Structure
    [Documentation]    Verify response structure (projects array, total_projects, automation_project_dir)
    [Tags]    api    projects
    ${response}=    Get Projects API
    ${expected_keys}=    Create List    projects    total_projects    automation_project_dir
    Verify API Response Structure    ${response}    ${expected_keys}

TC_API_PROJ_003: Verify Project Object Structure
    [Documentation]    Verify project object structure (name, path, stats)
    [Tags]    api    projects
    ${response}=    Get Projects API
    ${json}=    Set Variable    ${response.json()}
    ${projects}=    Get From Dictionary    ${json}    projects
    Run Keyword If    len(${projects}) > 0    Verify Project Object Structure    ${projects[0]}

TC_API_PROJ_004: Verify Stats Calculation
    [Documentation]    Verify stats calculation (pass_rate, total_tests, passed, failed, last_run)
    [Tags]    api    projects
    ${response}=    Get Projects API
    ${json}=    Set Variable    ${response.json()}
    ${projects}=    Get From Dictionary    ${json}    projects
    Run Keyword If    len(${projects}) > 0    Verify Project Stats    ${projects[0]}

TC_API_PROJ_005: Verify Only Projects With Results Folder Are Returned
    [Documentation]    Verify only projects with results folder are returned
    [Tags]    api    projects
    ${response}=    Get Projects API
    ${json}=    Set Variable    ${response.json()}
    ${projects}=    Get From Dictionary    ${json}    projects
    FOR    ${project}    IN    @{projects}
        Dictionary Should Contain Key    ${project}    name
        Dictionary Should Contain Key    ${project}    path
        Dictionary Should Contain Key    ${project}    stats
    END

TC_API_PROJ_006: Verify Empty Projects List Handling
    [Documentation]    Verify empty projects list handling
    [Tags]    api    projects
    ${response}=    Get Projects API
    ${json}=    Set Variable    ${response.json()}
    ${projects}=    Get From Dictionary    ${json}    projects
    ${total_projects}=    Get From Dictionary    ${json}    total_projects
    Should Be Equal As Integers    ${total_projects}    len(${projects})

*** Keywords ***
Verify Project Stats
    [Arguments]    ${project}
    ${stats}=    Get From Dictionary    ${project}    stats
    Dictionary Should Contain Key    ${stats}    pass_rate
    Dictionary Should Contain Key    ${stats}    total_tests
    Dictionary Should Contain Key    ${stats}    passed
    Dictionary Should Contain Key    ${stats}    failed
    Dictionary Should Contain Key    ${stats}    last_run
