*** Settings ***
Resource    ../variables/config.robot
Resource    ../variables/selectors.robot
Library    SeleniumLibrary

*** Variables ***
# Homepage Page Object - Locators
${HP_PAGE_TITLE}                QA Manager - Select Project
${HP_HEADER_TEXT}               QA Manager
${HP_SUBHEADER_TEXT}            เลือก Project ที่ต้องการดูผลการทดสอบ

# Project Card Locators (already in selectors.robot)
# ${HP_PROJECT_CARD}
# ${HP_PROJECT_NAME}
# ${HP_PROJECT_PASS_RATE}
# ${HP_PROJECT_TOTAL_TESTS}
# ${HP_PROJECT_LAST_RUN}

# State Locators (already in selectors.robot)
# ${HP_LOADING}
# ${HP_ERROR}
# ${HP_NO_PROJECTS}

*** Keywords ***
Verify Homepage Loaded
    [Documentation]    Verify homepage is loaded
    Title Should Be    ${HP_PAGE_TITLE}
    Wait Until Element Is Visible    ${HP_HEADER_TITLE}
    Element Should Contain    ${HP_HEADER_TITLE}    ${HP_HEADER_TEXT}

Verify Projects Grid Visible
    [Documentation]    Verify projects grid is visible
    Wait Until Element Is Visible    ${HP_PROJECTS_GRID}
    Element Should Be Visible    ${HP_PROJECTS_GRID}
