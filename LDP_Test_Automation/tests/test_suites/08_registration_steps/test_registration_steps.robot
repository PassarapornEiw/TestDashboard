*** Settings ***
Documentation    Test Suite for Registration Steps Info Module
Resource         ../../../resources/keywords/common_keywords.robot
Resource         ../../../resources/variables/common_variables.robot

Suite Setup       Initialize Browser
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Take Screenshot On Failure    ${TEST_NAME}

*** Test Cases ***
TC_REG_001: Verify Registration Steps Display
    [Documentation]    Test registration steps information display
    [Tags]    registration_steps
    Navigate To Page    registration_steps_info.html
    Page Should Contain    ขั้นตอนการลงทะเบียน
    Page Should Contain    กรอกแบบสอบถามความเสี่ยง
    Page Should Contain    อ่านและยอมรับสัญญา
