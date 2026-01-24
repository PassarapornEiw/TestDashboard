*** Settings ***
Resource    ../variables/config.robot
Resource    ../variables/selectors.robot
Library    SeleniumLibrary

*** Variables ***
# Dashboard Page Object - Locators
${DB_PAGE_TITLE}                Test Automation Dashboard
${DB_HEADER_TEXT}               🧪 Test Automation Dashboard
${DB_BACK_BUTTON_TEXT}          ← กลับหน้าแรก

# Summary Card IDs (already in selectors.robot)
# ${DB_CARD_TOTAL}
# ${DB_CARD_PASSED}
# ${DB_CARD_FAILED_MAJOR}
# ${DB_CARD_FAILED_BLOCK}
# ${DB_CARD_PASS_RATE}

# Chart and Info (already in selectors.robot)
# ${DB_PIE_CHART}
# ${DB_LATEST_RUN_INFO}

*** Keywords ***
Verify Dashboard Loaded
    [Documentation]    Verify dashboard is loaded
    Title Should Be    ${DB_PAGE_TITLE}
    Wait Until Element Is Visible    ${DB_HEADER}
    Element Should Contain    ${DB_HEADER_TITLE}    Test Automation Dashboard

Verify Dashboard URL
    [Documentation]    Verify dashboard URL contains project parameter
    [Arguments]    ${project_name}
    ${current_url}=    Get Location
    Should Contain    ${current_url}    /dashboard
    Should Contain    ${current_url}    project=${project_name}
