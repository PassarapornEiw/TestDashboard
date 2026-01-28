*** Settings ***
Documentation    Navigation keywords for page transitions
Resource         common_keywords.robot
Resource         authentication_keywords.robot
Resource         otp_keywords.robot
Resource         program_keywords.robot
Resource         ../page_objects/select_card_page.robot

*** Keywords ***
Navigate Through Full Flow
    [Documentation]    Navigate through complete flow
    [Arguments]    ${program_type}    ${id_card}    ${phone}    ${otp1}    ${otp2}    ${card_selection}    ${user_choice}    ${occupation}    ${reason}
    Navigate To Page    authentication.html
    Complete Authentication    ${id_card}    ${phone}
    Complete OTP1    ${otp1}
    Select Card    ${card_selection}
    Click Card Continue Button
    Select Program And Verify Details    ${program_type}    debt-restructuring

    Run Keyword If    '${user_choice}' == 'interested'    Select Interested In Offer
    Run Keyword If    '${user_choice}' == 'setNewPayment'    Select Set New Payment

    RETURN    Success

Verify Program Type Propagation
    [Documentation]    Verify program type is passed through all pages
    [Arguments]    ${program_type}
    ${current_url}=    Get Current URL
    Should Contain    ${current_url}    type=${program_type}
