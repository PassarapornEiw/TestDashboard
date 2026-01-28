*** Settings ***
Documentation    Page Object for Program Details Page
Resource         page_base.robot

*** Keywords ***
Navigate To Program Details Page
    [Documentation]    Navigate to program details page with program type
    [Arguments]    ${program_type}=debt re
    Go To    ${BASE_URL}${PROGRAM_DETAILS_PAGE}?type=${program_type}
    Wait For Page To Contain    สวัสดี คุณ

Verify Program Title
    [Documentation]    Verify program title
    [Arguments]    ${expected_title}
    Element Should Contain    ${PROGRAM_DETAILS_TITLE}    ${expected_title}

Verify Payment Conditions Visible
    [Documentation]    Verify payment conditions section is visible
    Element Should Be Visible    ${PAYMENT_CONDITIONS_SECTION}

Verify Payment Conditions Not Visible
    [Documentation]    Verify payment conditions section is not visible
    Element Should Not Be Visible    ${PAYMENT_CONDITIONS_SECTION}

Verify Contact Info Visible
    [Documentation]    Verify contact info is visible
    Element Should Be Visible    ${CONTACT_INFO_SECTION}
    Element Should Contain    ${CONTACT_INFO_SECTION}    02-777-1555

Verify Contact Info Not Visible
    [Documentation]    Verify contact info is not visible
    Element Should Not Be Visible    ${CONTACT_INFO_SECTION}

Click Interested Button
    [Documentation]    Click "สนใจในข้อเสนอนี้" button
    Click Button    ${BTN_INTERESTED}

Click Set New Payment Button
    [Documentation]    Click "กำหนดยอดผ่อนชำระใหม่" button
    Click Button    ${BTN_SET_NEW_PAYMENT}

Verify Navigated To Condition
    [Documentation]    Verify navigation to condition page
    Verify Navigation To Page    condition.html    ตรวจสอบเงื่อนไข

Verify Navigated To Set Payment
    [Documentation]    Verify navigation to set payment page
    Verify Navigation To Page    set_new_payment.html    กรอกยอดผ่อนชำระเพื่อรับข้อเสนอใหม่

Verify Debt Re Details
    [Documentation]    Verify debt re program details
    Verify Program Title    โครงการปรับปรุงโครงสร้างหนี้
    Verify Payment Conditions Not Visible
    Verify Contact Info Not Visible

Verify Rewrite Settlement Details
    [Documentation]    Verify rewrite settlement program details
    Verify Program Title    โครงการปรับปรุงโครงสร้างหนี้แบบมีส่วนลด
    Verify Payment Conditions Visible
    Verify Contact Info Visible
