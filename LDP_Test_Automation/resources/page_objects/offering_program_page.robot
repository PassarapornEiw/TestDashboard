*** Settings ***
Documentation    Page Object for Offering Program Page
Resource         page_base.robot

*** Keywords ***
Navigate To Offering Program Page
    [Documentation]    Navigate to offering program page with program type
    [Arguments]    ${program_type}=debt re
    Go To    ${BASE_URL}${OFFERING_PROGRAM_PAGE}?type=${program_type}
    Wait For Page To Contain    เลือกโครงการเพื่อดูรายละเอียดและเงื่อนไข
    # Wait for JavaScript to render programs
    Wait Until Element Is Visible    id=programList    timeout=15s
    Wait Until Element Is Visible    id=programCount    timeout=15s
    # Wait for program cards to be rendered (at least one radio button)
    Wait Until Page Contains Element    xpath=//input[@name='program']    timeout=15s

Verify Program Count
    [Documentation]    Verify program count message
    [Arguments]    ${expected_count}
    Wait Until Element Is Visible    id=programList    timeout=10s
    Wait Until Element Is Visible    id=programCount    timeout=10s
    Element Should Contain    id=programCount    ${expected_count}

Verify Program Count Message
    [Documentation]    Verify eligibility message shows correct program count
    [Arguments]    ${expected_count}
    ${message}=    Get Text    ${ELIGIBILITY_MESSAGE}
    Should Contain    ${message}    ${expected_count} โครงการ

Select Program
    [Documentation]    Select program by ID
    [Arguments]    ${program_id}
    Wait Until Element Is Visible    xpath=//input[@name='program' and @value='${program_id}']    timeout=10s
    Click Element    xpath=//input[@name='program' and @value='${program_id}']

Verify Program Selected
    [Documentation]    Verify program is selected (radio button is checked)
    [Arguments]    ${program_id}
    ${is_selected}=    Execute JavaScript    return document.querySelector("input[name='program'][value='${program_id}']").checked;
    Should Be True    ${is_selected}    Program ${program_id} should be selected

Verify Program Not Selected
    [Documentation]    Verify program is not selected (radio button is not checked)
    [Arguments]    ${program_id}
    ${is_selected}=    Execute JavaScript    return document.querySelector("input[name='program'][value='${program_id}']").checked;
    Should Not Be True    ${is_selected}    Program ${program_id} should not be selected

Verify Program Has Discount
    [Documentation]    Verify program shows discount amount
    [Arguments]    ${expected_discount}
    Element Should Contain    ${PROGRAM_LIST}    ${expected_discount}

Click Program Continue Button
    [Documentation]    Click continue button
    Click Continue Button    ${PROGRAM_CONTINUE_BUTTON}

Verify Navigated To Program Details
    [Documentation]    Verify navigation to program details page
    Verify Navigation To Page    program_details.html    สวัสดี คุณ

Verify Debt Re Display
    [Documentation]    Verify debt re program display (2 programs, none selected)
    Verify Program Count    2
    Verify Program Not Selected    debt-restructuring

Verify Rewrite Settlement Display
    [Documentation]    Verify rewrite settlement program display (1 program, selected, with discount)
    Verify Program Count    1
    Verify Program Selected    debt-restructuring-discount
    Verify Program Has Discount    83,666
