*** Settings ***
Resource    ../variables/config.robot
Library    RequestsLibrary
Library    Collections
Library    JSON

*** Keywords ***
Get Projects API
    [Documentation]    Call /api/projects endpoint
    ${response}=    GET    ${DASHBOARD_URL}${API_PROJECTS}
    RETURN    ${response}

Get Dashboard Data API
    [Documentation]    Call /api/data endpoint
    [Arguments]    ${project_name}=${EMPTY}
    ${params}=    Create Dictionary
    Run Keyword If    '${project_name}' != '${EMPTY}'    Set To Dictionary    ${params}    project    ${project_name}
    ${response}=    GET    ${DASHBOARD_URL}${API_DATA}    params=${params}
    RETURN    ${response}

Verify API Response Structure
    [Documentation]    Validate JSON structure
    [Arguments]    ${response}    ${expected_keys}
    ${status_code}=    Set Variable    ${response.status_code}
    Should Be Equal As Integers    ${status_code}    200
    ${json}=    Set Variable    ${response.json()}
    FOR    ${key}    IN    @{expected_keys}
        Dictionary Should Contain Key    ${json}    ${key}
    END

Verify API Status Code
    [Documentation]    Verify HTTP status code
    [Arguments]    ${response}    ${expected_code}=200
    ${status_code}=    Set Variable    ${response.status_code}
    Should Be Equal As Integers    ${status_code}    ${expected_code}

Get Excel Preview
    [Documentation]    Call /api/excel_preview endpoint
    [Arguments]    ${excel_path}
    ${params}=    Create Dictionary    path    ${excel_path}
    ${response}=    GET    ${DASHBOARD_URL}${API_EXCEL_PREVIEW}    params=${params}
    RETURN    ${response}

Export PDF
    [Documentation]    Call PDF export API
    [Arguments]    ${endpoint}    ${payload}
    ${headers}=    Create Dictionary    Content-Type    application/json
    ${response}=    POST    ${DASHBOARD_URL}${endpoint}    json=${payload}    headers=${headers}
    RETURN    ${response}

Export Test Case PDF
    [Documentation]    Call /api/export_testcase_pdf endpoint
    [Arguments]    ${test_case_data}
    ${response}=    Export PDF    ${API_EXPORT_TESTCASE_PDF}    ${test_case_data}
    RETURN    ${response}

Export Feature PDFs ZIP
    [Documentation]    Call /api/export_feature_pdfs_zip endpoint
    [Arguments]    ${feature_data}
    ${response}=    Export PDF    ${API_EXPORT_FEATURE_ZIP}    ${feature_data}
    RETURN    ${response}

Get Thumbnail
    [Documentation]    Call thumbnail API
    [Arguments]    ${file_path}
    ${params}=    Create Dictionary    path    ${file_path}
    ${response}=    GET    ${DASHBOARD_URL}${API_EVIDENCE_THUMBNAIL}    params=${params}
    RETURN    ${response}

Get Thumbnail Info
    [Documentation]    Call /api/thumbnail_info endpoint
    ${response}=    GET    ${DASHBOARD_URL}${API_THUMBNAIL_INFO}
    RETURN    ${response}

Verify Projects Response Structure
    [Documentation]    Verify /api/projects response structure
    [Arguments]    ${response}
    Verify API Status Code    ${response}    200
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    projects
    Dictionary Should Contain Key    ${json}    total_projects
    Dictionary Should Contain Key    ${json}    automation_project_dir
    ${projects}=    Get From Dictionary    ${json}    projects
    Should Be True    ${projects} is not None

Verify Project Object Structure
    [Documentation]    Verify project object structure
    [Arguments]    ${project}
    Dictionary Should Contain Key    ${project}    name
    Dictionary Should Contain Key    ${project}    path
    Dictionary Should Contain Key    ${project}    stats
    ${stats}=    Get From Dictionary    ${project}    stats
    Dictionary Should Contain Key    ${stats}    pass_rate
    Dictionary Should Contain Key    ${stats}    total_tests
    Dictionary Should Contain Key    ${stats}    passed
    Dictionary Should Contain Key    ${stats}    failed
    Dictionary Should Contain Key    ${stats}    last_run

Verify Dashboard Data Response Structure
    [Documentation]    Verify /api/data response structure
    [Arguments]    ${response}
    Verify API Status Code    ${response}    200
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    runs
    Dictionary Should Contain Key    ${json}    features
    Dictionary Should Contain Key    ${json}    test_cases
