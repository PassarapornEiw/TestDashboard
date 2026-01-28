*** Settings ***
Documentation    Keywords for Program selection and details
Resource         common_keywords.robot
Resource         ../page_objects/offering_program_page.robot
Resource         ../page_objects/program_details_page.robot

*** Keywords ***
Select Program And Verify Details
    [Documentation]    Select program and verify details based on program type
    [Arguments]    ${program_type}    ${program_id}
    Navigate To Offering Program Page    ${program_type}

    Run Keyword If    '${program_type}' == 'debt re'    Verify Debt Re Display
    Run Keyword If    '${program_type}' == 'rewrite settlement'    Verify Rewrite Settlement Display

    Select Program    ${program_id}
    Click Program Continue Button
    Verify Navigated To Program Details

    Run Keyword If    '${program_type}' == 'debt re'    Verify Debt Re Details
    Run Keyword If    '${program_type}' == 'rewrite settlement'    Verify Rewrite Settlement Details

Verify Program Type In Flow
    [Documentation]    Verify program type is maintained throughout the flow
    [Arguments]    ${program_type}
    ${url}=    Get Current URL
    ${encoded_type}=    Evaluate    '${program_type}'.replace(' ', '%20')
    Should Contain    ${url}    type=${encoded_type}

Select Interested In Offer
    [Documentation]    Select "สนใจในข้อเสนอนี้" option
    Click Interested Button
    program_details_page.Verify Navigated To Condition

Select Set New Payment
    [Documentation]    Select "กำหนดยอดผ่อนชำระใหม่" option
    Click Set New Payment Button
    program_details_page.Verify Navigated To Set Payment
