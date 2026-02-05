*** Settings ***
Documentation    Test Suite for Authentication Module.
...               Requires the LDP app server at base_url (e.g. run run_tests_with_server.bat or start server in "LDP Project" with: python server.py 5000).
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/keywords/authentication_keywords.robot
Resource         ../../../resources/page_objects/authentication_page.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_AUTH_001: Valid Authentication
    [Documentation]    Test valid ID card and phone number authentication
    [Tags]    smoke    authentication
    ${test_data}=    Get Test Case Data By ID    TC_AUTH_001
    Navigate To Authentication Page
    Fill Authentication Form    ${test_data}[ID_Card]    ${test_data}[Phone_Number]
    Click Auth Continue Button
    Verify Navigated To OTP1
    Update Test Result    TC_AUTH_001    Pass

TC_AUTH_002: Invalid ID Card Format
    [Documentation]    Test invalid ID card format validation
    [Tags]    authentication    validation
    ${test_data}=    Get Test Case Data By ID    TC_AUTH_002
    Navigate To Authentication Page
    ${id_card}=    Get From Dictionary    ${test_data}    ID_Card    default=123456789
    ${phone}=    Get From Dictionary    ${test_data}    Phone_Number    default=082-999-9999
    ${error_msg}=    Get From Dictionary    ${test_data}    Expected_Error_Message    default=คุณกรอกข้อมูลผิดรูปแบบ
    Enter ID Card    ${id_card}
    Enter Phone Number    ${phone}
    Click Auth Continue Button Expecting Error
    Verify ID Card Error Message    ${error_msg}
    Update Test Result    TC_AUTH_002    Pass

TC_AUTH_005: Account Locked After 5 Failed Attempts
    [Documentation]    Test account lockout after 5 failed attempts
    [Tags]    authentication    error
    ${test_data}=    Get Test Case Data By ID    TC_AUTH_005
    Verify Account Locked
    Verify Navigated To Account Locked
    Update Test Result    TC_AUTH_005    Pass

TC_AUTH_MULTI_URL: Multi-URL demo (Google, Facebook, YouTube)
    [Documentation]    ทดสอบการเปิดสลับ 3 URLs ที่ดึงจาก LDP_UI.yaml (google_url_demo, facebook_url_demo, youtube_url_demo)
    [Tags]    multi_url    demo
    Run Multi URL Demo Flow
