*** Settings ***
Documentation    Keywords for Risk Questionnaire dynamic form handling
Resource          common_keywords.robot
Resource          ../page_objects/risk_questionnaire_page.robot

*** Keywords ***
Fill Questionnaire Based On Occupation
    [Arguments]    ${occupation}    ${company_name}=${EMPTY}    ${position}=${EMPTY}    ${years}=${EMPTY}    ${months}=${EMPTY}    ${income}=${EMPTY}    ${work_phone}=${EMPTY}    ${extension}=${EMPTY}    ${mobile_phone}=${EMPTY}    ${email}=${EMPTY}
    [Documentation]    Fill questionnaire form based on occupation type
    Navigate To Risk Questionnaire Page
    Select Occupation    ${occupation}
    # Wait for dynamic fields container to be updated
    Wait Until Element Is Visible    id=dynamicFields    timeout=10s
    
    Run Keyword If    '${company_name}' != '${EMPTY}'    Fill Company Name    ${company_name}
    Run Keyword If    '${position}' != '${EMPTY}'    Fill Position    ${position}
    Run Keyword If    '${years}' != '${EMPTY}'    Fill Work Years    ${years}
    Run Keyword If    '${months}' != '${EMPTY}'    Fill Work Months    ${months}
    Run Keyword If    '${income}' != '${EMPTY}'    Fill Monthly Income    ${income}
    Run Keyword If    '${work_phone}' != '${EMPTY}'    Fill Work Phone    ${work_phone}
    Run Keyword If    '${extension}' != '${EMPTY}'    Fill Extension    ${extension}
    Run Keyword If    '${mobile_phone}' != '${EMPTY}'    Fill Mobile Phone    ${mobile_phone}
    Run Keyword If    '${email}' != '${EMPTY}'    Fill Email    ${email}

Fill Questionnaire For Private Employee
    [Arguments]    ${company_name}    ${position}    ${years}    ${months}    ${income}    ${work_phone}    ${extension}    ${mobile_phone}    ${email}    ${reason}
    [Documentation]    Fill questionnaire for private employee
    Fill Questionnaire Based On Occupation    private_employee    ${company_name}    ${position}    ${years}    ${months}    ${income}    ${work_phone}    ${extension}    ${mobile_phone}    ${email}
    Select Reason    ${reason}

Fill Questionnaire For Freelance
    [Arguments]    ${position}    ${years}    ${months}    ${income}    ${mobile_phone}    ${email}    ${reason}
    [Documentation]    Fill questionnaire for freelance
    Fill Questionnaire Based On Occupation    freelance    position=${position}    years=${years}    months=${months}    income=${income}    mobile_phone=${mobile_phone}    email=${email}
    Select Reason    ${reason}

Verify Review Page Data
    [Arguments]    &{expected_data}
    [Documentation]    Verify review page shows correct data
    Click Continue Button
    Verify Review Page Visible
    
    FOR    ${key}    ${value}    IN    &{expected_data}
        Verify Review Item    ${key}    ${value}
    END

Change Occupation And Verify Fields Cleared
    [Arguments]    ${old_occupation}    ${new_occupation}
    [Documentation]    Change occupation and verify all fields are cleared
    Select Occupation    ${old_occupation}
    Fill Position    Test Position
    Fill Monthly Income    50000
    Select Occupation    ${new_occupation}
    Verify All Fields Cleared






