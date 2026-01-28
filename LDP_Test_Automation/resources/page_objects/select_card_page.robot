*** Settings ***
Documentation    Page Object for Select Credit Card Page
Resource         page_base.robot

*** Keywords ***
Navigate To Select Card Page
    [Documentation]    Navigate to select credit card page
    Go To    ${BASE_URL}${SELECT_CARD_PAGE}
    Wait For Page To Contain    เลือกบัตรที่ต้องการตรวจสอบ

Select Card
    [Documentation]    Select credit card by value (card1/card2/card3) or by card number (extract first4/last4 and match on-screen)
    [Arguments]    ${card_ref}
    ${card_str}=    Convert To String    ${card_ref}
    ${digits}=    Evaluate    ''.join(c for c in '''${card_str}''' if c.isdigit())
    ${digits_len}=    Get Length    ${digits}
    Run Keyword If    ${digits_len} >= 8    Select Card By First And Last Four From Digits    ${digits}
    Run Keyword If    ${digits_len} < 8    Click Element    xpath=//input[@name='creditCard' and @value='${card_ref}']

Select Card By First And Last Four From Digits
    [Documentation]    Helper: parse digits into first4/last4 and call Select Card By First And Last Four
    [Arguments]    ${digits}
    ${first4}=    Evaluate    '''${digits}'''[:4]
    ${last4}=    Evaluate    '''${digits}'''[-4:]
    Select Card By First And Last Four    ${first4}    ${last4}

Select Card By First And Last Four
    [Documentation]    Find card on screen whose div.card-number first4/last4 match, then select it (first match; log WARN if multiple)
    [Arguments]    ${first4}    ${last4}
    ${count}=    Get Element Count    xpath=//label[contains(@class,'card-option') and not(contains(@class,'disabled'))]
    ${match_indices}=    Create List
    FOR    ${i}    IN RANGE    1    ${count}+1
        ${div_xpath}=    Set Variable    (//label[contains(@class,'card-option') and not(contains(@class,'disabled'))]//div[contains(@class,'card-number')])[${i}]
        ${text}=    Get Text    xpath=${div_xpath}
        ${digits}=    Evaluate    ''.join(c for c in '''${text}''' if c.isdigit())
        ${len_d}=    Get Length    ${digits}
        Continue For Loop If    ${len_d} < 8
        ${f4}=    Evaluate    '''${digits}'''[:4]
        ${l4}=    Evaluate    '''${digits}'''[-4:]
        ${match}=    Evaluate    '''${f4}'''=='''${first4}''' and '''${l4}'''=='''${last4}'''
        Run Keyword If    ${match}    Append To List    ${match_indices}    ${i}
    END
    ${match_count}=    Get Length    ${match_indices}
    Run Keyword If    ${match_count} == 0    Fail    No card on screen matched first4=${first4} last4=${last4}
    Run Keyword If    ${match_count} > 1    Log    Found multiple cards matching first4=${first4} last4=${last4}; selecting the first one.    WARN
    ${first_match}=    Get From List    ${match_indices}    0
    Click Element    xpath=(//label[contains(@class,'card-option') and not(contains(@class,'disabled'))]//input[@name='creditCard'])[${first_match}]

Verify Card Disabled
    [Documentation]    Verify card is disabled (registered)
    [Arguments]    ${card_value}
    ${card_element}=    Get WebElement    xpath=//input[@name='creditCard' and @value='${card_value}']
    Element Should Be Disabled    ${card_element}
    Element Should Be Visible    xpath=//label[contains(@class, 'disabled') and .//input[@value='${card_value}']]

Verify Card Enabled
    [Documentation]    Verify card is enabled
    [Arguments]    ${card_value}
    ${card_element}=    Get WebElement    xpath=//input[@name='creditCard' and @value='${card_value}']
    Element Should Be Enabled    ${card_element}

Click Card Continue Button
    [Documentation]    Click continue button
    Click Continue Button    ${CARD_CONTINUE_BUTTON}

Verify Navigated To Offering Program
    [Documentation]    Verify navigation to offering program page
    Verify Navigation To Page    offering_program.html    เลือกโครงการเพื่อดูรายละเอียดและเงื่อนไข

Verify Program Type In URL
    [Documentation]    Verify program type is in URL
    [Arguments]    ${program_type}
    ${current_url}=    Get Location
    ${encoded_type}=    Evaluate    '${program_type}'.replace(' ', '%20')
    Should Contain    ${current_url}    type=${encoded_type}
