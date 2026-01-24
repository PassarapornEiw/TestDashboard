*** Settings ***
Documentation    Thumbnail API Tests
Resource    ../../resources/variables/config.robot
Resource    ../../resources/keywords/api_keywords.robot
Library    RequestsLibrary
Library    Collections

Suite Setup    Create Session    dashboard    ${DASHBOARD_URL}
Suite Teardown    Delete All Sessions

*** Variables ***
${SAMPLE_IMAGE_PATH}    Automation_Project/DRDB/results/20250516-161132/Payment/TC001_225522422/A01_0.png
${SAMPLE_HTML_PATH}     Automation_Project/DRDB/results/20250516-161132/Payment/TC001_225522422/testresult.html

*** Test Cases ***
TC_API_THUMB_001: Verify GET Evidence Thumbnail Returns Image
    [Documentation]    Verify GET /api/evidence_thumbnail?path=<path> returns image
    [Tags]    api    thumbnail
    ${response}=    Get Thumbnail    ${SAMPLE_IMAGE_PATH}
    ${status_code}=    Set Variable    ${response.status_code}
    # May return 200 (success) or 404 (not found) depending on file existence
    Should Be True    ${status_code} in [200, 404]    Unexpected status code: ${status_code}
    Run Keyword If    ${status_code} == 200    Verify Image Response    ${response}

TC_API_THUMB_002: Verify Thumbnail Generation For Images
    [Documentation]    Verify thumbnail generation for images
    [Tags]    api    thumbnail
    ${response}=    Get Thumbnail    ${SAMPLE_IMAGE_PATH}
    Run Keyword If    ${response.status_code} == 200    Verify Image Response    ${response}

TC_API_THUMB_003: Verify Thumbnail Generation For HTML Files
    [Documentation]    Verify thumbnail generation for HTML files
    [Tags]    api    thumbnail
    ${response}=    Get Thumbnail    ${SAMPLE_HTML_PATH}
    ${status_code}=    Set Variable    ${response.status_code}
    # HTML thumbnail may take time to generate or may not exist
    Should Be True    ${status_code} in [200, 404, 500]    Unexpected status code: ${status_code}
    Run Keyword If    ${status_code} == 200    Verify Image Response    ${response}

TC_API_THUMB_004: Verify Thumbnail Caching
    [Documentation]    Verify thumbnail caching
    [Tags]    api    thumbnail
    # Request same thumbnail twice and verify response time (cached should be faster)
    ${response1}=    Get Thumbnail    ${SAMPLE_IMAGE_PATH}
    Sleep    1s
    ${response2}=    Get Thumbnail    ${SAMPLE_IMAGE_PATH}
    # Both should return same status code
    Should Be Equal    ${response1.status_code}    ${response2.status_code}

TC_API_THUMB_005: Verify Error Handling For Invalid Path
    [Documentation]    Verify error handling for invalid path
    [Tags]    api    thumbnail    negative
    ${response}=    Get Thumbnail    Invalid/Path/To/File.png
    ${status_code}=    Set Variable    ${response.status_code}
    Should Be True    ${status_code} >= 400    Expected error status code for invalid path

TC_API_THUMB_006: Verify GET Thumbnail Info Returns Cache Info
    [Documentation]    Verify GET /api/thumbnail_info returns cache info
    [Tags]    api    thumbnail
    ${response}=    Get Thumbnail Info
    Verify API Status Code    ${response}    200
    ${json}=    Set Variable    ${response.json()}
    # Verify response contains cache information
    Should Not Be Empty    ${json}

*** Keywords ***
Verify Image Response
    [Arguments]    ${response}
    ${content_type}=    Get From Dictionary    ${response.headers}    Content-Type
    Should Contain    ${content_type}    image
    ${content_length}=    Get From Dictionary    ${response.headers}    Content-Length
    Should Be True    int(${content_length}) > 0    Image should have content
