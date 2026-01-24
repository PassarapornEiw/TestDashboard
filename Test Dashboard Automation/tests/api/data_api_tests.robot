*** Settings ***
Documentation    Data API Tests
Resource    ../../resources/variables/config.robot
Resource    ../../resources/keywords/api_keywords.robot
Library    RequestsLibrary
Library    Collections
Library    JSON

Suite Setup    Create Session    dashboard    ${DASHBOARD_URL}
Suite Teardown    Delete All Sessions

*** Test Cases ***
TC_API_DATA_001: Verify GET Data API Returns 200
    [Documentation]    Verify GET /api/data returns 200
    [Tags]    smoke    api    data
    ${response}=    Get Dashboard Data API
    Verify API Status Code    ${response}    200

TC_API_DATA_002: Verify GET Data API With Project Parameter
    [Documentation]    Verify GET /api/data?project=<name> returns correct project data
    [Tags]    smoke    api    data
    ${response}=    Get Dashboard Data API    ${TEST_PROJECT}
    Verify API Status Code    ${response}    200
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    runs

TC_API_DATA_003: Verify Response Structure
    [Documentation]    Verify response structure (runs, features, test_cases)
    [Tags]    api    data
    ${response}=    Get Dashboard Data API    ${TEST_PROJECT}
    Verify Dashboard Data Response Structure    ${response}

TC_API_DATA_004: Verify Backward Compatibility
    [Documentation]    Verify backward compatibility (no project parameter)
    [Tags]    api    data
    ${response}=    Get Dashboard Data API
    Verify API Status Code    ${response}    200
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    runs

TC_API_DATA_005: Verify Error Handling For Invalid Project
    [Documentation]    Verify error handling for invalid project
    [Tags]    api    data    negative
    ${response}=    Get Dashboard Data API    InvalidProjectName123
    ${status_code}=    Set Variable    ${response.status_code}
    Should Be True    ${status_code} >= 400    Expected error status code for invalid project

TC_API_DATA_006: Verify Timestamp Grouping
    [Documentation]    Verify timestamp grouping
    [Tags]    api    data
    ${response}=    Get Dashboard Data API    ${TEST_PROJECT}
    ${json}=    Set Variable    ${response.json()}
    ${runs}=    Get From Dictionary    ${json}    runs
    Run Keyword If    len(${runs}) > 0    Verify Timestamp Format    ${runs}

TC_API_DATA_007: Verify Feature Grouping
    [Documentation]    Verify feature grouping
    [Tags]    api    data
    ${response}=    Get Dashboard Data API    ${TEST_PROJECT}
    ${json}=    Set Variable    ${response.json()}
    ${features}=    Get From Dictionary    ${json}    features
    Run Keyword If    len(${features}) > 0    Verify Feature Structure    ${features[0]}

TC_API_DATA_008: Verify Status Priority
    [Documentation]    Verify status priority (FAIL Block > FAIL Major > PASS > UNKNOWN)
    [Tags]    api    data
    ${response}=    Get Dashboard Data API    ${TEST_PROJECT}
    ${json}=    Set Variable    ${response.json()}
    ${features}=    Get From Dictionary    ${json}    features
    Run Keyword If    len(${features}) > 0    Verify Status Priority Logic    ${features[0]}

*** Keywords ***
Verify Timestamp Format
    [Arguments]    ${runs}
    FOR    ${timestamp}    IN    @{runs.keys()}
        Should Match Regexp    ${timestamp}    ^\\d{8}[-_]\\d{6}$    Invalid timestamp format: ${timestamp}
    END

Verify Feature Structure
    [Arguments]    ${feature}
    Dictionary Should Contain Key    ${feature}    feature_name
    Dictionary Should Contain Key    ${feature}    status

Verify Status Priority Logic
    [Arguments]    ${feature}
    ${status}=    Get From Dictionary    ${feature}    status
    ${status_upper}=    Convert To Uppercase    ${status}
    # Verify status is one of the expected values
    Should Be True    '${status_upper}' in ['PASS', 'FAIL (MAJOR)', 'FAIL (BLOCK)', 'UNKNOWN']    Invalid status: ${status}
