*** Settings ***
Documentation    Page Object for Success Page
Resource         page_base.robot

*** Keywords ***
Navigate To Success Page
    [Documentation]    Navigate to success page
    Go To    ${BASE_URL}${SUCCESS_PAGE}
    Wait For Page To Contain    ลงทะเบียนสำเร็จ

Verify Success Message
    [Documentation]    Verify success message is displayed
    Page Should Contain    ลงทะเบียนสำเร็จ
    Page Should Contain    คำขอของคุณได้รับการบันทึกเรียบร้อยแล้ว

Verify Reference Number
    [Documentation]    Verify reference number is displayed
    Element Should Be Visible    ${REFERENCE_NUMBER}
    ${ref_number}=    Get Text    ${REFERENCE_NUMBER}
    Should Match Regexp    ${ref_number}    REF\\d+

Click Finish Button
    [Documentation]    Click finish button
    Click Button    ${BTN_FINISH}

Verify Navigated To Authentication
    [Documentation]    Verify navigation back to authentication
    Wait Until Location Contains    authentication.html
