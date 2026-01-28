*** Settings ***
Documentation    Page Object for Risk Questionnaire Page
Resource         page_base.robot

*** Keywords ***
Navigate To Risk Questionnaire Page
    [Documentation]    Navigate to risk questionnaire page
    Go To    ${BASE_URL}${RISK_QUESTIONNAIRE_PAGE}
    Wait For Page To Contain    แบบสอบถามความเสี่ยง

Select Occupation
    [Documentation]    Select occupation from dropdown
    [Arguments]    ${occupation}
    Select From List By Value    ${OCCUPATION_DROPDOWN}    ${occupation}

Select Reason
    [Documentation]    Select reason from dropdown
    [Arguments]    ${reason}
    Select From List By Value    ${REASON_DROPDOWN}    ${reason}

Fill Company Name
    [Documentation]    Fill company name field (if visible)
    [Arguments]    ${company_name}
    ${element}=    Get WebElements    xpath=//input[@id='companyName']
    ${count}=    Get Length    ${element}
    Run Keyword If    ${count} > 0    Input Text    id=companyName    ${company_name}

Fill Position
    [Documentation]    Fill position field
    [Arguments]    ${position}
    Input Text    id=position    ${position}

Fill Work Years
    [Documentation]    Fill work years
    [Arguments]    ${years}
    Input Text    id=workYears    ${years}

Fill Work Months
    [Documentation]    Fill work months
    [Arguments]    ${months}
    Input Text    id=workMonths    ${months}

Fill Monthly Income
    [Documentation]    Fill monthly income
    [Arguments]    ${income}
    Input Text    id=monthlyIncome    ${income}

Fill Work Phone
    [Documentation]    Fill work phone (if visible)
    [Arguments]    ${phone}
    ${element}=    Get WebElements    xpath=//input[@id='workPhone']
    ${count}=    Get Length    ${element}
    Run Keyword If    ${count} > 0    Input Text    id=workPhone    ${phone}

Fill Extension
    [Documentation]    Fill extension (if visible)
    [Arguments]    ${extension}
    ${element}=    Get WebElements    xpath=//input[@id='extension']
    ${count}=    Get Length    ${element}
    Run Keyword If    ${count} > 0    Input Text    id=extension    ${extension}

Fill Mobile Phone
    [Documentation]    Fill mobile phone
    [Arguments]    ${phone}
    Input Text    id=mobilePhone    ${phone}

Fill Email
    [Documentation]    Fill email
    [Arguments]    ${email}
    Input Text    id=email    ${email}

Click Risk Continue Button
    [Documentation]    Click continue button to show review
    Click Continue Button    ${RISK_CONTINUE_BUTTON}
    # Wait for review page to be shown
    Wait Until Element Is Visible    ${REVIEW_CONTENT}    timeout=10s

Verify Review Page Visible
    [Documentation]    Verify review page is displayed
    Wait Until Element Is Visible    ${REVIEW_CONTENT}    timeout=10s
    Element Should Be Visible    ${REVIEW_CONTENT}
    Page Should Contain    ตรวจสอบข้อมูลของท่าน

Verify Review Item
    [Documentation]    Verify review item shows correct value
    [Arguments]    ${label}    ${value}
    Element Should Contain    ${REVIEW_CONTENT}    ${label}
    Element Should Contain    ${REVIEW_CONTENT}    ${value}

Click Edit Button
    [Documentation]    Click edit button to go back to form
    Click Button    ${BTN_EDIT}

Click Confirm Button
    [Documentation]    Click confirm button
    Wait Until Element Is Visible    ${BTN_CONFIRM}    timeout=10s
    Click Button    ${BTN_CONFIRM}

Verify Navigated To E-Contract
    [Documentation]    Verify navigation to E-Contract page
    Wait Until Location Contains    e_contract_and_t_c.html

Verify All Fields Cleared
    [Documentation]    Verify all fields are cleared when occupation changes
    ${company_value}=    Get Value    id=companyName
    ${position_value}=    Get Value    id=position
    Should Be Empty    ${company_value}
    Should Be Empty    ${position_value}
