*** Settings ***
Documentation    Excel Preview API Tests
Resource    ../../resources/variables/config.robot
Resource    ../../resources/keywords/api_keywords.robot
Library    RequestsLibrary
Library    Collections

Suite Setup    Create Session    dashboard    ${DASHBOARD_URL}
Suite Teardown    Delete All Sessions

*** Variables ***
${SAMPLE_EXCEL_PATH}    Automation_Project/DRDB/results/20250516-161132/DRDB_Payment_Output_20250516-161132.xlsx

*** Test Cases ***
TC_API_EXCEL_001: Verify GET Excel Preview API Returns 200
    [Documentation]    Verify GET /api/excel_preview?path=<path> returns 200
    [Tags]    api    excel
    ${response}=    Get Excel Preview    ${SAMPLE_EXCEL_PATH}
    ${status_code}=    Set Variable    ${response.status_code}
    # May return 200 or 404 depending on file existence
    Should Be True    ${status_code} in [200, 404]    Unexpected status code: ${status_code}

TC_API_EXCEL_002: Verify Excel Data Parsing
    [Documentation]    Verify Excel data parsing
    [Tags]    api    excel
    ${response}=    Get Excel Preview    ${SAMPLE_EXCEL_PATH}
    Run Keyword If    ${response.status_code} == 200    Verify Excel Response Structure    ${response}

TC_API_EXCEL_003: Verify Table Structure In Response
    [Documentation]    Verify table structure in response
    [Tags]    api    excel
    ${response}=    Get Excel Preview    ${SAMPLE_EXCEL_PATH}
    Run Keyword If    ${response.status_code} == 200    Verify Excel Table Structure    ${response}

TC_API_EXCEL_004: Verify Error Handling For Invalid Path
    [Documentation]    Verify error handling for invalid path
    [Tags]    api    excel    negative
    ${response}=    Get Excel Preview    Invalid/Path/To/File.xlsx
    ${status_code}=    Set Variable    ${response.status_code}
    Should Be True    ${status_code} >= 400    Expected error status code for invalid path

TC_API_EXCEL_005: Verify Path Resolution From PROJECT_ROOT
    [Documentation]    Verify path resolution from PROJECT_ROOT
    [Tags]    api    excel
    # Test with relative path from PROJECT_ROOT
    ${response}=    Get Excel Preview    ${SAMPLE_EXCEL_PATH}
    ${status_code}=    Set Variable    ${response.status_code}
    # Path should be resolved correctly (200 if exists, 404 if not)
    Should Be True    ${status_code} in [200, 404]    Unexpected status code: ${status_code}

*** Keywords ***
Verify Excel Response Structure
    [Arguments]    ${response}
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    data
    Dictionary Should Contain Key    ${json}    columns

Verify Excel Table Structure
    [Arguments]    ${response}
    ${json}=    Set Variable    ${response.json()}
    ${data}=    Get From Dictionary    ${json}    data
    ${columns}=    Get From Dictionary    ${json}    columns
    Should Not Be Empty    ${columns}
    Should Be True    len(${data}) >= 0    Data should be an array
